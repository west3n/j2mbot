import asyncio
import datetime
import decouple
import handlers.commands

from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageIdentifierNotSpecified
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from handlers import commands, google
from keyboards import inline
from database import users, balance, output, binance_db, stabpool


class NewWallet(StatesGroup):
    wallet = State()
    amount = State()
    email = State()


class ChangeWallet(StatesGroup):
    email = State()
    wallet = State()


class ChangePercentage(StatesGroup):
    percentage = State()


async def withdraw_main_menu(call: types.CallbackQuery):
    try:
        await call.message.delete()
    except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
        pass
    photo = decouple.config("BANNER_WITHDRAWAL")
    current_date = datetime.datetime.now()
    week_number = (current_date.day - 1) // 7 + 1
    is_even_week = week_number % 2 == 0
    amount, out = await balance.get_amount(call.from_user.id, "Коллективный аккаунт")
    balance_ = await balance.get_balance(call.from_user.id)
    body = amount + out
    income = (balance_[0] + balance_[1]) - body
    language = await users.user_data(call.from_user.id)
    first_trans = await balance.get_first_transaction(call.from_user.id, "Коллективный аккаунт")
    date_first = first_trans[2] if first_trans is not None else None
    hold = await balance.get_hold(call.from_user.id)
    hold = hold[0] if hold is not None else 0
    withdrawal_date = date_first + datetime.timedelta(days=hold) if date_first and hold else None
    now = datetime.datetime.now()
    now = now.replace(tzinfo=datetime.timezone.utc)
    if withdrawal_date:
        if now <= date_first + datetime.timedelta(days=hold):
            withdrawal_balance = income
        else:
            withdrawal_balance = balance_[0] + balance_[1]
    else:
        if balance_[0] + balance_[1] >= 1000:
            withdrawal_balance = balance_[0] + balance_[1]
        else:
            withdrawal_balance = 0
    if is_even_week is False and datetime.datetime.now().weekday() == 0:
        date_withdraw = datetime.datetime.now().strftime("%d.%m.%Y")
    else:
        now_weekday = datetime.datetime.now().weekday()
        days_until_monday = (7 - now_weekday) % 7
        days_until_monday = 7 if days_until_monday == 0 else days_until_monday
        date_withdraw = (datetime.datetime.now() + datetime.timedelta(days=days_until_monday))
        week_number = (date_withdraw.day - 1) // 7 + 1
        is_even_week_withdraw = week_number % 2 == 0
        if is_even_week_withdraw is True:
            date_withdraw = date_withdraw + datetime.timedelta(days=7)
            date_withdraw = date_withdraw.date().strftime("%d.%m.%Y")
        else:
            date_withdraw = date_withdraw.date().strftime("%d.%m.%Y")
    try:
        amount_st, out_st = await balance.get_amount(call.from_user.id, "Стабилизационный пул")
        balance_st = await stabpool.get_balance(call.from_user.id)
        body_st = amount_st + out_st
        income_st = (balance_st[0] + balance_st[1]) - body_st
        first_trans_st = await balance.get_first_transaction(call.from_user.id, "Стабилизационный пул")
        date_first_st = first_trans_st[2] if first_trans_st is not None else None
        hold_st = await stabpool.get_hold(call.from_user.id)
        hold_st = hold_st[0] if hold_st is not None else 0
        withdrawal_date_st = date_first_st + datetime.timedelta(days=hold_st) if date_first_st and hold_st else None
        if withdrawal_date_st:
            if now <= date_first_st + datetime.timedelta(days=hold_st):
                withdrawal_balance_st = income_st
            else:
                withdrawal_balance_st = balance_st[0] + balance_st[1]
        else:
            if balance_st[0] + balance_st[1] >= 1000:
                withdrawal_balance_st = balance_[0] + balance_[1]
            else:
                withdrawal_balance_st = 0
        stabpool_balance_user = round(withdrawal_balance_st, 2)
    except TypeError:
        stabpool_balance_user = 0
        withdrawal_date_st = None

    text = f"<em>[Коллективный аккаунт]</em> \n<b>Баланс, доступный к выводу:" \
           f"</b> {round(withdrawal_balance, 2) if withdrawal_balance > 0 else 0} USDT"
    text += f"\n<b>Дата окончания холда:" \
            f"</b> {withdrawal_date.strftime('%d.%m.%Y %H:%M')} GMT" if withdrawal_date else ""
    text += f"\n\n<em>[Стабилизационный пул]</em> \n<b>Баланс, доcтупный к выводу:</b>"\
            f"{stabpool_balance_user}" if stabpool_balance_user > 0 else ""
    text += f"\n<b>Дата окончания холда:" \
            f"</b> {withdrawal_date_st.strftime('%d.%m.%Y %H:%M')} GMT" if withdrawal_date_st else ""
    text += f"\n\n<b>Дата возможного перечисления:</b> {date_withdraw}"

    if language[4] == 'EN':
        photo = decouple.config("BANNER_WITHDRAWAL_EN")
        text = f"<b>Available withdrawal balance:</b>" \
               f" {round(withdrawal_balance, 2) if withdrawal_balance > 0 else 0} USDT"
        text += f"\n<b>Hold end date:</b> " \
                f"{withdrawal_date.strftime('%d.%m.%Y %H:%M')} GMT" if withdrawal_date else ""
        text += f"\n<b>Possible transfer date:</b> {date_withdraw}"
    await call.message.answer_photo(photo=photo, caption=text, reply_markup=inline.main_withdraw(language[4]))


async def change_wallet_new(call: types.CallbackQuery, state: FSMContext):
    code = commands.generate_random_code()
    email = await users.check_email(call.from_user.id)
    language = await users.user_data(call.from_user.id)
    if email:
        parts = email[0].split('@')
        username = parts[0]
        domain = parts[1]
        masked_username = username[:3] + '*' * (len(username) - 3)
        masked_email = masked_username + '@' + domain
        text = f'📧 Вам на почту {masked_email} отправлен код подтверждения смены кошелька, ' \
               f'введите его в ответном сообщении:'
        email_text = f"Вас приветствует команда DAO J2M!\n\n" \
                     f"Для смены кошелька отправьте боту этот код: {code}" \
                     f"\n\nЕсли у вас возникли сложности, или вам нужна помощь, вы можете связаться с нами по " \
                     f"этой электронной почте ответным письмом, или напишите нам в телеграм: " \
                     f"https://t.me/J2M_Support "
        await google.send_email_message(to=email[0],
                                        subject="DAO J2M change wallet",
                                        message_text=email_text)
        if language[4] == "EN":
            text = f"You have been sent a confirmation code to your " \
                   f"email {email[0]}. Please enter it in your reply message:"
    else:
        text = 'Произошла ошибка, связанная с отсутствием email в вашем профиле. Обратитесь в тех.поддержку'
        if language[4] == "EN":
            text = "An error occurred due to the absence of an email in your profile. Please contact technical support."
    await call.message.delete()
    email_message = await call.message.answer(text)
    await ChangeWallet.email.set()
    async with state.proxy() as data:
        data['code'] = code
        data['email_message'] = email_message.message_id


async def change_wallet_step1(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        if msg.text == data['code']:
            try:
                await msg.delete()
            except MessageToDeleteNotFound:
                pass
            try:
                await msg.bot.delete_message(msg.chat.id, data.get('email_message'))
            except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
                pass
            text = "👛 Пришлите новый адрес криптокошелька TRON TRC-20 для вывода:"
            if language[4] == 'EN':
                text = "👛 Please provide a new cryptocurrency wallet TRON TRC-20 address for withdrawal:"
            second_message = await msg.answer(text)
            data['second_message'] = second_message.message_id
            await ChangeWallet.next()
        else:
            try:
                await msg.delete()
            except MessageToDeleteNotFound:
                pass
            try:
                await msg.bot.delete_message(msg.chat.id, data.get('email_message'))
            except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
                pass
            text = f'🚫 Введённый код {msg.text} не совпадает с тем, который был отправлен на почту, попробуйте ' \
                   f'еще раз!'
            if language[4] == 'EN':
                text = f"🚫 The entered code {msg.text} does not match the one that was " \
                       f"sent to your email. Please try again!"
            error_message = await msg.answer(text)
            data['error_message'] = error_message.message_id


async def change_wallet_step2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        language = await users.user_data(msg.from_user.id)
        await users.save_wallet(msg.text, msg.from_id)
        text = "Кошелек успешно обновлен!"
        if language[4] == 'EN':
            text = "Wallet successfully updated!"
        try:
            await msg.delete()
        except MessageToDeleteNotFound:
            pass
        try:
            await msg.bot.delete_message(msg.chat.id, data.get('second_message'))
        except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
            pass
        try:
            await msg.bot.delete_message(msg.chat.id, data.get('error_message'))
        except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
            pass
        await msg.answer(text, reply_markup=inline.main_withdraw(language[4]))
        await state.finish()


async def change_percentage(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    reinvest = await balance.get_percentage(call.from_user.id)
    await call.message.delete()
    text = "📈 Выберите процент, который вы хотите реинвестировать после каждой торговой недели:\n\n" \
           f"<em>В данный момент вы реинвестируете: {reinvest}%</em>"
    if language[4] == 'EN':
        text = "Wallet successfully updated!"
    await call.message.answer(text, reply_markup=inline.withdraw_percentage(language[4]))
    await ChangePercentage.percentage.set()


async def change_percentage_step2(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    await balance.update_percentage(call.from_user.id, int(call.data))
    await call.message.delete()
    text = f"Процент реинвестирования успешно изменен на {call.data}%!"
    if language[4] == 'EN':
        text = "Reinvestment percentage successfully updated!"
    await call.answer(text, show_alert=True)
    await withdraw_main_menu(call)
    username = call.from_user.username
    await call.bot.send_message(
        decouple.config("GROUP_ID"),
        f'Пользователь {"@" + username if username is not None else call.from_user.id} ' 
        f'изменил процент реинвестирования на - {call.data}%')
    await state.finish()


async def withdrawal_handler(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    language = await users.user_data(call.from_user.id)
    binance_balance = await binance_db.get_binance_ac(call.from_user.id)
    if binance_balance:
        text = f"🔀 Выберите тип аккаунта для вывода средств:"
        if language[4] == "EN":
            text = "🔀 Select the account type for fund withdrawal:"
        await call.message.answer(text, reply_markup=inline.withdrawal_account(language[4]))
    else:
        await withdrawal_handler_collective(call, state)


async def withdrawal_handler_personal(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    binance_balance = await binance_db.get_binance_ac(call.from_user.id)
    wallet = await users.user_data(call.from_user.id)
    language = await users.user_data(call.from_user.id)

    if wallet[6]:
        if binance_balance[1] >= 50:
            text = f"<b>Баланс, доступный к выводу:</b> {binance_balance[1]} USDT" \
                   f"\nCумма минимального вывода 50 USDT" \
                   f"\n\n💳 Напишите сумму USDT, которую хотите вывести:"
            if language[4] == "EN":
                text = f"The balance available for withdrawal: {binance_balance[1]} USDT" \
                       f"\nMinimum withdrawal amount is 50 USDT." \
                       f"\n\n💳 Please write the amount of USDT you want to withdraw:"
            del_msg = await call.message.answer(text, reply_markup=inline.back_menu(language[4]))
            await state.set_state(NewWallet.amount.state)
            await state.update_data({"del_msg": del_msg.message_id, "status": "Личный"})
        else:

            photo = decouple.config("BANNER_WITHDRAWAL")
            text = f"<b>Баланс:</b> {binance_balance[1]} USDT" \
                   f"\n\n<em>❗Cумма минимального вывода 50 USDT </em> "
            alert = "❗Cумма минимального вывода 50 USDT"
            if language[4] == "EN":
                photo = decouple.config("BANNER_WITHDRAWAL_EN")
                text = f"<b>Balance:</b> {binance_balance[1]} USDT" \
                       f"\n\n<em>❗Minimum withdrawal amount is 50 USDT</em>"
                alert = "❗Minimum withdrawal amount is 50 USDT"
            await call.answer(alert, show_alert=True)
            await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))
    else:
        photo = decouple.config("BANNER_WITHDRAWAL")
        text = "❗️Для вывода средств <b>необходимо добавить кошелек для вывода.</b>" \
               "\n\n<em>Нажмите кнопку ниже для добавления кошелька! " \
               "Вы всегда можете изменить кошелек для вывода в этом меню.</em>"
        alert = "❗️Для вывода средств необходимо добавить кошелек для вывода!"
        if language[4] == "EN":
            photo = decouple.config("BANNER_WITHDRAWAL_EN")
            text = "❗️To withdraw funds, <b>you need to add a withdrawal wallet.</b>" \
                   "\n\n<em>Click the button below to add a wallet!" \
                   "You can always change the withdrawal wallet in this menu.</em>"
            alert = "❗️To withdraw funds, you need to add a withdrawal wallet!"
        await call.answer(alert, show_alert=True)
        await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))


async def withdrawal_handler_collective(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    amount, out = await balance.get_amount(call.from_user.id, "Коллективный аккаунт")
    balance_ = await balance.get_balance(call.from_user.id)
    body = amount + out
    income = (balance_[0] + balance_[1]) - body
    language = await users.user_data(call.from_user.id)
    first_trans = await balance.get_first_transaction(call.from_user.id, "Коллективный аккаунт")
    date_first = first_trans[2] if first_trans is not None else None
    hold = await balance.get_hold(call.from_user.id)
    hold = hold[0] if hold is not None else 0
    withdrawal_date = date_first + datetime.timedelta(days=hold) if date_first and hold else None
    now = datetime.datetime.now()
    now = now.replace(tzinfo=datetime.timezone.utc)
    if withdrawal_date:
        if now <= date_first + datetime.timedelta(days=hold):
            withdrawal_balance = income
        else:
            withdrawal_balance = balance_[0] + balance_[1]
    else:
        if balance_[0] + balance_[1] >= 1000:
            withdrawal_balance = balance_[0] + balance_[1]
        else:
            withdrawal_balance = 0
    if first_trans:
        wallet = await users.user_data(call.from_user.id)
        if wallet[6]:
            if withdrawal_balance > 50:
                text = f"<b>Баланс, доступный к выводу:</b> {round(withdrawal_balance, 2)} USDT" \
                       f"\nCумма минимального вывода 50 USDT" \
                       f"\n\n💳 Напишите сумму USDT, которую хотите вывести:"
                if language[4] == "EN":
                    text = f"<b>Available withdrawal balance:</b> {round(withdrawal_balance, 2)} USDT" \
                           f"\nMinimum withdrawal amount: 50 USDT" \
                           f"\n\n💳 Please enter the amount of USDT you want to withdraw:"
                del_msg = await call.message.answer(text)
                await state.set_state(NewWallet.amount.state)
                await state.update_data({"del_msg": del_msg.message_id, "status": "Коллективный"})
            else:
                photo = decouple.config("BANNER_WITHDRAWAL")
                text = f"<b>Баланс, доступный к выводу:" \
                       f"</b> {round(withdrawal_balance, 2) if withdrawal_balance>0 else 0} USDT" \
                       f"\n\n<em>❗Cумма минимального вывода 50 USDT </em> "
                alert = "❗Cумма минимального вывода 50 USDT!"
                if language[4] == "EN":
                    photo = decouple.config("BANNER_WITHDRAWAL_EN")
                    text = f"❗️<b>Available withdrawal balance:</b> " \
                           f"{withdrawal_balance if withdrawal_balance>0 else 0} USDT" \
                           f"\n\n<em>❗Minimum withdrawal amount is 50 USDT</em>"
                    alert = "❗Minimum withdrawal amount is 50 USDT!"
                await call.answer(alert, show_alert=True)
                await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))
        else:
            photo = decouple.config("BANNER_WITHDRAWAL")
            text = "❗️Для вывода средств <b>необходимо добавить кошелек для вывода.</b>" \
                   "\n\n<em>Нажмите кнопку ниже для добавления кошелька! " \
                   "Вы всегда можете изменить кошелек для вывода в этом меню.</em>"
            alert = "❗️Для вывода средств необходимо добавить кошелек для вывода!"
            if language[4] == "EN":
                photo = decouple.config("BANNER_WITHDRAWAL_EN")
                text = "❗️To withdraw funds, <b>you need to add a withdrawal wallet.</b>" \
                       "\n\n<em>Click the button below to add a wallet!" \
                       "You can always change the withdrawal wallet in this menu.</em>"
                alert = "❗️To withdraw funds, you need to add a withdrawal wallet!"
            await call.answer(alert, show_alert=True)
            await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))
    else:
        photo = decouple.config("BANNER_WITHDRAWAL")
        text = "❗️Для активации функции вывода средств <b>нужно пополнить Баланс.</b>" \
               "\n\n<em>В данный момент у вас нет Истории Пополнений!</em>"
        alert = "❗️Для активации функции вывода средств нужно пополнить Баланс."
        if language[4] == "EN":
            photo = decouple.config("BANNER_WITHDRAWAL_EN")
            text = "❗To activate the withdrawal function, you need to replenish your balance." \
                   "\n\n <em>Currently, you have no Deposit History!</em>"
            alert = "❗To activate the withdrawal function, you need to replenish your balance!"
        await call.answer(alert, show_alert=True)
        await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))


async def withdrawal_handler_stabpool(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    amount, out = await balance.get_amount(call.from_user.id, "Стабилизационный пул")
    balance_ = await stabpool.get_balance(call.from_user.id)
    body = amount + out
    income = (balance_[0] + balance_[1]) - body
    language = await users.user_data(call.from_user.id)
    first_trans = await balance.get_first_transaction(call.from_user.id, "Стабилизационный пул")
    date_first = first_trans[2] if first_trans is not None else None
    hold = await stabpool.get_hold(call.from_user.id)
    hold = hold[0] if hold is not None else 0
    withdrawal_date = date_first + datetime.timedelta(days=hold) if date_first and hold else None
    now = datetime.datetime.now()
    now = now.replace(tzinfo=datetime.timezone.utc)
    if withdrawal_date:
        if now <= date_first + datetime.timedelta(days=hold):
            withdrawal_balance = income
        else:
            withdrawal_balance = balance_[0] + balance_[1]
    else:
        if balance_[0] + balance_[1] >= 1000:
            withdrawal_balance = balance_[0] + balance_[1]
        else:
            withdrawal_balance = 0
    if first_trans:
        wallet = await users.user_data(call.from_user.id)
        if wallet[6]:
            if withdrawal_balance > 50:
                text = f"<b>Баланс, доступный к выводу:</b> {round(withdrawal_balance, 2)} USDT" \
                       f"\nCумма минимального вывода 50 USDT" \
                       f"\n\n💳 Напишите сумму USDT, которую хотите вывести:"
                if language[4] == "EN":
                    text = f"<b>Available withdrawal balance:</b> {round(withdrawal_balance, 2)} USDT" \
                           f"\nMinimum withdrawal amount: 50 USDT" \
                           f"\n\n💳 Please enter the amount of USDT you want to withdraw:"
                del_msg = await call.message.answer(text)
                await state.set_state(NewWallet.amount.state)
                await state.update_data({"del_msg": del_msg.message_id, "status": "Стабпул"})
            else:
                photo = decouple.config("BANNER_WITHDRAWAL")
                text = f"<b>Баланс, доступный к выводу:" \
                       f"</b> {round(withdrawal_balance, 2) if withdrawal_balance>0 else 0} USDT" \
                       f"\n\n<em>❗Cумма минимального вывода 50 USDT </em> "
                alert = "❗Cумма минимального вывода 50 USDT!"
                if language[4] == "EN":
                    photo = decouple.config("BANNER_WITHDRAWAL_EN")
                    text = f"❗️<b>Available withdrawal balance:</b> " \
                           f"{withdrawal_balance if withdrawal_balance > 0 else 0} USDT" \
                           f"\n\n<em>❗Minimum withdrawal amount is 50 USDT</em>"
                    alert = "❗Minimum withdrawal amount is 50 USDT!"
                await call.answer(alert, show_alert=True)
                await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))
        else:
            photo = decouple.config("BANNER_WITHDRAWAL")
            text = "❗️Для вывода средств <b>необходимо добавить кошелек для вывода.</b>" \
                   "\n\n<em>Нажмите кнопку ниже для добавления кошелька! " \
                   "Вы всегда можете изменить кошелек для вывода в этом меню.</em>"
            alert = "❗️Для вывода средств необходимо добавить кошелек для вывода!"
            if language[4] == "EN":
                photo = decouple.config("BANNER_WITHDRAWAL_EN")
                text = "❗️To withdraw funds, <b>you need to add a withdrawal wallet.</b>" \
                       "\n\n<em>Click the button below to add a wallet!" \
                       "You can always change the withdrawal wallet in this menu.</em>"
                alert = "❗️To withdraw funds, you need to add a withdrawal wallet!"
            await call.answer(alert, show_alert=True)
            await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))
    else:
        photo = decouple.config("BANNER_WITHDRAWAL")
        text = "❗️Для активации функции вывода средств <b>нужно пополнить Баланс.</b>" \
               "\n\n<em>В данный момент у вас нет Истории Пополнений!</em>"
        alert = "❗️Для активации функции вывода средств нужно пополнить Баланс."
        if language[4] == "EN":
            photo = decouple.config("BANNER_WITHDRAWAL_EN")
            text = "❗To activate the withdrawal function, you need to replenish your balance." \
                   "\n\n <em>Currently, you have no Deposit History!</em>"
            alert = "❗To activate the withdrawal function, you need to replenish your balance!"
        await call.answer(alert, show_alert=True)
        await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))


async def handle_amount(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    try:
        async with state.proxy() as data:
            await msg.delete()
            await msg.bot.delete_message(msg.from_id, data.get('del_msg'))
    except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
        pass
    if not msg.text.isdigit():
        text = 'Пожалуйста, используйте только цифры!\n\n' \
               '💳 Напишите сумму еще раз, минимальная сумма вывода - 50 USDT'
        if language[4] == 'EN':
            text = 'Please, use digits only!'
        await msg.answer(text)
    else:
        personal_balance_user = await binance_db.get_binance_ac(msg.from_user.id)
        async with state.proxy() as data:
            data['amount'] = msg.text
            if data.get("status") == "Личный":
                user_balance = personal_balance_user[1]
            elif data.get("status") == "Коллективный":
                amount, out = await balance.get_amount(msg.from_user.id, "Коллективный аккаунт")
                balance_ = await balance.get_balance(msg.from_user.id)
                body = amount + out
                income = (balance_[0] + balance_[1]) - body
                language = await users.user_data(msg.from_user.id)
                first_trans = await balance.get_first_transaction(msg.from_user.id, "Коллективный аккаунт")
                date_first = first_trans[2] if first_trans is not None else None
                hold = await balance.get_hold(msg.from_user.id)
                hold = hold[0] if hold is not None else 0
                withdrawal_date = date_first + datetime.timedelta(days=hold) if date_first and hold else None
                now = datetime.datetime.now()
                now = now.replace(tzinfo=datetime.timezone.utc)
                if withdrawal_date:
                    if now <= date_first + datetime.timedelta(days=hold):
                        withdrawal_balance = income
                    else:
                        withdrawal_balance = balance_[0] + balance_[1]
                else:
                    if balance_[0] + balance_[1] >= 1000:
                        withdrawal_balance = balance_[0] + balance_[1]
                    else:
                        withdrawal_balance = 0
                collective_balance_user = round(withdrawal_balance, 2)
                user_balance = collective_balance_user
            else:
                amount, out = await balance.get_amount(msg.from_user.id, "Стабилизационный пул")
                balance_ = await stabpool.get_balance(msg.from_user.id)
                body = amount + out
                income = (balance_[0] + balance_[1]) - body
                language = await users.user_data(msg.from_user.id)
                first_trans = await balance.get_first_transaction(msg.from_user.id, "Стабилизационный пул")
                date_first = first_trans[2] if first_trans is not None else None
                hold = await stabpool.get_hold(msg.from_user.id)
                hold = hold[0] if hold is not None else 0
                withdrawal_date = date_first + datetime.timedelta(days=hold) if date_first and hold else None
                now = datetime.datetime.now()
                now = now.replace(tzinfo=datetime.timezone.utc)
                if withdrawal_date:
                    if now <= date_first + datetime.timedelta(days=hold):
                        withdrawal_balance = income
                    else:
                        withdrawal_balance = balance_[0] + balance_[1]
                else:
                    if balance_[0] + balance_[1] >= 1000:
                        withdrawal_balance = balance_[0] + balance_[1]
                    else:
                        withdrawal_balance = 0
                stabpool_balance_user = round(withdrawal_balance, 2)
                user_balance = stabpool_balance_user
            if user_balance >= int(msg.text):
                wallet = await users.user_data(msg.from_user.id)
                text = f"Вы заказываете вывод {data.get('amount')} USDT на TRC-20 кошелёк {wallet[6]}"
                if language[4] == "EN":
                    text = f"You are requesting a withdrawal of {data.get('amount')} USDT to TRC-20 wallet {wallet[6]}"
                await msg.answer(text, reply_markup=inline.finish_withdrawal(language[4]))
            else:
                text = f'❗️<b>Сумма, доступная к выводу:</b> {user_balance} USDT!\n\n' \
                       '💳 Напишите сумму еще раз, минимальная сумма вывода - 50 USDT'
                if language[4] == 'EN':
                    text = f'❗️<b>Available withdrawal amount:</b> {user_balance} USDT!\n\n' \
                           '💳 Please enter the amount again, the minimum withdrawal amount is 50 USDT.'
                del_msg = await msg.answer(text)
                await state.update_data({"del_msg": del_msg.message_id})


async def finish_withdrawal(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    await call.bot.send_chat_action(call.message.chat.id, 'typing')
    if call.data == 'back':
        await state.finish()
        photo = decouple.config("BANNER_WITHDRAWAL")
        text = "Выберите пункт для продолжения."
        if language[4] == 'EN':
            photo = decouple.config("BANNER_WITHDRAWAL_EN")
            text = "Select an option to proceed."
        await call.message.answer_photo(photo=photo, caption=text, reply_markup=inline.main_withdraw(language[4]))
    elif call.data == 'confirm_withdrawal':
        async with state.proxy() as data:
            code = commands.generate_random_code()
            email = await users.check_email(call.from_user.id)
            wallet = await users.user_data(call.from_user.id)
            parts = email[0].split('@')
            username = parts[0]
            domain = parts[1]
            masked_username = username[:3] + '*' * (len(username) - 3)
            masked_email = masked_username + '@' + domain
            if email:
                data['code'] = code
                text = f'🏧 Заявка на сумму: {data.get("amount")} USDT\n' \
                       f'Кошелек вывода: {wallet[6]}' \
                       f'\n\n📧Пришлите код, отправленный на почту {masked_email} для подтверждения вывода:'
                if language[4] == 'EN':
                    text = f'Your withdrawal request for the amount of: {data.get("amount")} USDT has been accepted.' \
                           f'\nExpect a message regarding the results of your application review.'
                email_text = f"Вы заказываете вывод средств {data.get('amount')} USDT на кошелек {wallet[6]} !\n\n" \
                             f"Для подтверждения создания заявки отправьте боту этот код: {code}" \
                             f"\n\nЕсли у вас возникли сложности, или вам нужна помощь, вы можете связаться с нами по" \
                             f" этой электронной почте ответным письмом, или напишите нам в телеграм: " \
                             f"https://t.me/J2M_Support "
                await google.send_email_message(to=email[0],
                                                subject="DAO J2M withdrawal",
                                                message_text=email_text)
                await NewWallet.next()
            else:
                text = 'Произошла ошибка, связанная с отсутствием email в вашем профиле. Обратитесь в тех.поддержку'
                if language[4] == "EN":
                    text = "An error occurred due to the absence of an email in your profile. " \
                           "Please contact technical support."
                await state.finish()
            email_message = await call.message.answer(text)
            data['email_message'] = email_message.message_id
    else:
        text = 'Вы отменили операцию!'
        if language[4] == "EN":
            text = 'Operation canceled!'
        lol = await call.message.answer(text)
        await asyncio.sleep(2)
        await call.bot.delete_message(call.from_user.id, lol.message_id)
        await state.finish()
        await handlers.commands.bot_start_call(call)


async def confirm_email_withdrawal(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        wallet = await users.user_data(msg.from_user.id)
        if msg.text == data.get('code'):
            try:
                await msg.delete()
            except MessageToDeleteNotFound:
                pass
            try:
                await msg.bot.delete_message(msg.chat.id, data.get('email_message'))
            except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
                pass
            try:
                await msg.bot.delete_message(msg.chat.id, data.get('error_message'))
            except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
                pass
            await output.insert_new_output(msg.from_user.id, data.get('amount'), wallet[6])
            await balance.save_withdrawal_amount(data.get('amount'), msg.from_user.id)
            username = msg.from_user.username
            text = f'Ваша заявка на сумму: {data.get("amount")} USDT принята к рассмотрению!\n\n' \
                   f'<em>Ожидайте одобрения администратора!</em>'
            await msg.bot.send_message(
                decouple.config("GROUP_ID"),
                f'Пользователь {"@" + username if username is not None else msg.from_user.id} '
                f'отправил заявку на вывод средств:\n<b>Cумма:</b> {data.get("amount")}'
                f'\n<b>Кошелёк TRC-20:</b> {wallet[6]}'
                f'\n\nПодробнее по ссылке: http://89.223.121.160:8000/admin/app/output/'
                f'\n\nИнструкция: Подтвердите транзакцию и добавьте хэш транзакции!')
            await msg.answer(text, reply_markup=inline.main_withdraw(language[4]))
            await state.finish()
        else:
            try:
                await msg.delete()
            except MessageToDeleteNotFound:
                pass
            try:
                await msg.bot.delete_message(msg.chat.id, data.get('email_message'))
            except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
                pass
            try:
                await msg.bot.delete_message(msg.chat.id, data.get('error_message'))
            except (MessageToDeleteNotFound, MessageIdentifierNotSpecified):
                pass
            text = f'🚫 Введённый код {msg.text} не совпадает с тем, который был отправлен на почту, попробуйте ' \
                   f'еще раз!'
            if language[4] == 'EN':
                text = f"🚫 The entered code {msg.text} does not match the one that was " \
                       f"sent to your email. Please try again!"
            error_message = await msg.answer(text)
            data['error_message'] = error_message.message_id


def register(dp: Dispatcher):
    dp.register_callback_query_handler(withdraw_main_menu, text='withdrawal')
    dp.register_callback_query_handler(withdrawal_handler, text='withdrawal_funds')
    dp.register_callback_query_handler(withdrawal_handler_collective, text="withdrawal_500")
    dp.register_callback_query_handler(withdrawal_handler_personal, text="withdrawal_15000")
    dp.register_callback_query_handler(withdrawal_handler_stabpool, text='withdrawal_stabpool')
    dp.register_callback_query_handler(change_wallet_new, text='change_wallet')
    dp.register_callback_query_handler(change_percentage, text='change_percentage')
    dp.register_callback_query_handler(change_percentage_step2, state=ChangePercentage.percentage)
    dp.register_message_handler(change_wallet_step1, state=ChangeWallet.email)
    dp.register_message_handler(change_wallet_step2, state=ChangeWallet.wallet)
    dp.register_message_handler(handle_amount, state=NewWallet.amount)
    dp.register_callback_query_handler(finish_withdrawal, state=NewWallet.amount)
    dp.register_message_handler(confirm_email_withdrawal, state=NewWallet.email)
