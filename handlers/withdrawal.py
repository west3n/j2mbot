import asyncio
import datetime
import decouple
from aiogram.utils.exceptions import MessageToDeleteNotFound

import handlers.commands

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import inline
from database import users, balance, output, binance_db


class NewWallet(StatesGroup):
    wallet = State()
    amount = State()


class ChangeWallet(StatesGroup):
    wallet = State()


class ChangePercentage(StatesGroup):
    percentage = State()


async def withdraw_main_menu(call: types.CallbackQuery):
    await call.message.delete()
    photo = decouple.config("BANNER_WITHDRAWAL")
    language = await users.user_data(call.from_user.id)
    text = "Выберите пункт для продолжения."
    if language[4] == 'EN':
        photo = decouple.config("BANNER_WITHDRAWAL_EN")
        text = "Select an option to proceed."
    await call.message.answer_photo(photo=photo, caption=text, reply_markup=inline.main_withdraw(language[4]))


async def change_wallet_new(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    text = "👛 Пришлите новый адрес криптокошелька TRON TRC-20 для вывода:"
    if language[4] == 'EN':
        text = "👛 Please provide a new cryptocurrency wallet TRON TRC-20 address for withdrawal:"
    await call.message.answer(text)
    await ChangeWallet.wallet.set()


async def change_wallet_step2(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    await users.save_wallet(msg.text, msg.from_id)
    text = "Кошелек успешно обновлен!"
    if language[4] == 'EN':
        text = "Wallet successfully updated!"
    await msg.answer(text, reply_markup=inline.main_withdraw(language[4]))
    await state.finish()


async def change_percentage(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    text = "📈 Выберите процент, который вы хотите реинвестировать после каждой торговой недели:\n\n" \
           "<em>По умолчанию реинвестируется 100%</em>"
    if language[4] == 'EN':
        text = "Wallet successfully updated!"
    await call.message.answer(text, reply_markup=inline.withdraw_percentage(language[4]))
    await ChangePercentage.percentage.set()


async def change_percentage_step2(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    await balance.update_percentage(call.from_user.id, int(call.data))
    await call.message.delete()
    text = "Процент реинвестирования успешно изменен!"
    if language[4] == 'EN':
        text = "Reinvestment percentage successfully updated!"
    await call.message.answer(text, reply_markup=inline.main_withdraw(language[4]))
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
            if language[4] == "EN":
                photo = decouple.config("BANNER_WITHDRAWAL_EN")
                text = f"<b>Balance:</b> {binance_balance[1]} USDT" \
                       f"\n\n<em>❗Minimum withdrawal amount is 50 USDT</em>"
            await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))
    else:
        photo = decouple.config("BANNER_WITHDRAWAL")
        text = "❗️Для вывода средств <b>необходимо добавить кошелек для вывода.</b>" \
               "\n\n<em>Нажмите кнопку ниже для добавления кошелька! " \
               "Вы всегда можете изменить кошелек для вывода в этом меню.</em>"
        if language[4] == "EN":
            photo = decouple.config("BANNER_WITHDRAWAL_EN")
            text = "❗️To withdraw funds, <b>you need to add a withdrawal wallet.</b>" \
                   "\n\n<em>Click the button below to add a wallet!" \
                   "You can always change the withdrawal wallet in this menu.</em>"
        await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))


async def withdrawal_handler_collective(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    language = await users.user_data(call.from_user.id)
    first_trans = await balance.get_first_transaction(call.from_user.id)
    date_first = first_trans[2] if first_trans is not None else None
    if first_trans:
        wallet = await users.user_data(call.from_user.id)
        if wallet[6]:
            balance_user, deposit, withdraw, referral_balance = await balance.get_balance(call.from_user.id)
            if balance_user > 0:
                if withdraw == 0:
                    now = datetime.datetime.now()
                    if now.tzinfo is None:
                        now = now.replace(tzinfo=datetime.timezone.utc)
                    hold = await balance.get_hold(call.from_user.id)
                    hold = hold[0] if hold is not None else 0
                    if hold == 0:
                        if first_trans[3] > 1000:
                            pass
                        else:
                            if balance_user > 1000:
                                text = f"<b>Баланс, доступный к выводу:</b> {balance_user} USDT" \
                                       f"\nCумма минимального вывода 50 USDT" \
                                       f"\n\n💳 Напишите сумму USDT, которую хотите вывести:"
                                if language[4] == 'EN':
                                    text = f"The balance available for withdrawal: {balance_user} USDT" \
                                           f"\nMinimum withdrawal amount is 50 USDT." \
                                           f"\n\n💳 Please write the amount of USDT you want to withdraw:"
                                del_msg = await call.message.answer(text, reply_markup=inline.back_menu(language[4]))
                                await state.set_state(NewWallet.amount.state)
                                await state.update_data({"del_msg": del_msg.message_id, "status": "Коллективный"})
                            else:
                                photo = decouple.config("BANNER_WITHDRAWAL")
                                text = f"<b>Баланс:</b> {balance_user} USDT" \
                                       f"\n\n<em>❗Ваш баланс должен быть больше 1000 USDT, " \
                                       f"так как ваше пополнение было на сумму от 500 USDT!" \
                                       f"\nПодробнее об условиях можно прочитать в разделе 'Пополнение' или " \
                                       f"'Информация'</em>"
                                if language[4] == "EN":
                                    photo = decouple.config("BANNER_WITHDRAWAL_EN")
                                    text = f"<b>Balance:</b> {balance_user} USDT" \
                                           f"\n\n<em>❗️Your balance should be greater than 1000 USDT, " \
                                           f"since your deposit was in the amount of 500 USDT!" \
                                           f"\nFor more information about the conditions, please refer to the " \
                                           f"'Deposit' or 'Information' section.</em>"
                                await call.message.answer_photo(photo, text,
                                                                reply_markup=inline.main_withdraw(language[4]))
                    elif date_first + datetime.timedelta(days=hold) <= now:
                        text = f"<b>Баланс, доступный к выводу:</b> {balance_user} USDT" \
                               f"\nCумма минимального вывода 50 USDT" \
                               f"\n\n💳 Напишите сумму USDT, которую хотите вывести:"
                        if language[4] == 'EN':
                            text = f"The balance available for withdrawal: {balance_user} USDT" \
                                   f"\nMinimum withdrawal amount is 50 USDT." \
                                   f"\n\n💳 Please write the amount of USDT you want to withdraw:"
                        del_msg = await call.message.answer(text, reply_markup=inline.back_menu(language[4]))
                        await state.set_state(NewWallet.amount.state)
                        await state.update_data({"del_msg": del_msg.message_id, "status": "Коллективный"})
                    else:
                        if deposit >= balance_user:
                            text = f"<b>Баланс, доступный к выводу:</b> {balance_user} USDT" \
                                   f"\nCумма минимального вывода 50 USDT" \
                                   f"\n\n💳 Напишите сумму USDT, которую хотите вывести:"
                            if language[4] == 'EN':
                                text = f"The balance available for withdrawal: {balance_user} USDT" \
                                       f"\nMinimum withdrawal amount is 50 USDT." \
                                       f"\n\n💳 Please write the amount of USDT you want to withdraw:"
                            del_msg = await call.message.answer(text, reply_markup=inline.back_menu(language[4]))
                            await state.set_state(NewWallet.amount.state)
                            await state.update_data({"del_msg": del_msg.message_id, "status": "Коллективный"})
                        else:
                            photo = decouple.config("BANNER_WITHDRAWAL")
                            withdrawal_date = date_first + datetime.timedelta(days=hold)
                            text = f"<b>Баланс:</b> {balance_user} USDT\n\n❗<b>Ближайшая дата для вывода:</b> " \
                                   f"{withdrawal_date.strftime('%d-%m-%Y %H:%M:%S')} GMT." \
                                   f"\n\n<em> Вы можете поменять настройки реинвестирования по кнопке ниже!</em>"
                            if language[4] == "EN":
                                photo = decouple.config("BANNER_WITHDRAWAL_EN")
                                text = f"️<b>Balance:</b> {balance_user} USDT\n\n❗<b>Next withdrawal date:</b> " \
                                       f"{withdrawal_date.strftime('%d-%m-%Y %H:%M:%S')} GMT.\n\n<em>You can change " \
                                       f"the reinvestment settings by clicking the button below!</em>"
                            await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))
                else:
                    photo = decouple.config("BANNER_WITHDRAWAL")
                    text = f"<b>Баланс, зарезервированный для вывода:</b> {withdraw} USDT" \
                           f"\n\n<em>❗У вас есть зарезервированная сумма для вывода, " \
                           f"пожалуйста, ожидайте поступления средств!</em>"
                    if language[4] == "EN":
                        photo = decouple.config("BANNER_WITHDRAWAL_EN")
                        text = f"<b>Reserved balance for withdrawal:</b> {withdraw} USDT" \
                               f"\n\n<em>❗️You have a reserved amount for withdrawal, please wait for the " \
                               f"funds to be credited!</em>"
                    await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))
            else:
                photo = decouple.config("BANNER_WITHDRAWAL")
                withdrawal_date = date_first + datetime.timedelta(days=14)
                text = f"<b>Баланс:</b> {balance_user} USDT" \
                       f"\n\n<b>Ближайшая дата для вывода:</b> {withdrawal_date.strftime('%d-%m-%Y %H:%M:%S')} GMT" \
                       f"\n\n<em>❗Cумма минимального вывода 50 USDT </em> "
                if language[4] == "EN":
                    photo = decouple.config("BANNER_WITHDRAWAL_EN")
                    text = f"❗️<b>Balance:</b> {balance_user} USDT" \
                           f"\n\n⏰ <b>Next withdrawal date:</b> {withdrawal_date.strftime('%d-%m-%Y %H:%M:%S')} GMT" \
                           f"\n\n<em>❗Minimum withdrawal amount is 50 USDT</em>"
                await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))
        else:
            photo = decouple.config("BANNER_WITHDRAWAL")
            text = "❗️Для вывода средств <b>необходимо добавить кошелек для вывода.</b>" \
                   "\n\n<em>Нажмите кнопку ниже для добавления кошелька! " \
                   "Вы всегда можете изменить кошелек для вывода в этом меню.</em>"
            if language[4] == "EN":
                photo = decouple.config("BANNER_WITHDRAWAL_EN")
                text = "❗️To withdraw funds, <b>you need to add a withdrawal wallet.</b>" \
                       "\n\n<em>Click the button below to add a wallet!" \
                       "You can always change the withdrawal wallet in this menu.</em>"
            await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))
    else:
        photo = decouple.config("BANNER_WITHDRAWAL")
        text = "❗️Для активации функции вывода средств <b>нужно пополнить Баланс.</b>" \
               "\n\n<em>В данный момент у вас нет Истории Пополнений!</em>"
        if language[4] == "EN":
            photo = decouple.config("BANNER_WITHDRAWAL_EN")
            text = "❗To activate the withdrawal function, you need to replenish your balance." \
                   "\n\n <em>Currently, you have no Deposit History!</em>"
        await call.message.answer_photo(photo, text, reply_markup=inline.main_withdraw(language[4]))


async def handle_amount(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    try:
        async with state.proxy() as data:
            await msg.delete()
            await msg.bot.delete_message(msg.from_id, data.get('del_msg'))
    except MessageToDeleteNotFound:
        pass
    if not msg.text.isdigit():
        text = 'Пожалуйста, используйте только цифры!\n\n' \
               '💳 Напишите сумму еще раз, минимальная сумма вывода - 50 USDT'
        if language[4] == 'EN':
            text = 'Please, use digits only!'
        await msg.answer(text)
    else:
        personal_balance_user = await binance_db.get_binance_ac(msg.from_user.id)
        collective_balance_user = await balance.get_balance(msg.from_user.id)
        async with state.proxy() as data:
            data['amount'] = msg.text
            if data.get("status") == "Личный":
                user_balance = personal_balance_user[1]
            else:
                user_balance = collective_balance_user[0]
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
        wallet = await users.user_data(call.from_user.id)
        async with state.proxy() as data:
            await output.insert_new_output(call.from_user.id, data.get('amount'), wallet[6])
            await balance.save_withdrawal_amount(data.get('amount'), call.from_user.id)
            text = f'Ваша заявка на сумму: {data.get("amount")} USDT принята' \
                   '\nОтслеживать статус заявки Вы можете в меню "История выводов"'
            if language[4] == 'EN':
                text = f'Your withdrawal request for the amount of: {data.get("amount")} USDT has been accepted.' \
                       '\nYou can track the status of your request in the "Withdrawal History" menu.'
        await call.message.answer(text, reply_markup=inline.back_button(language[4]))
        wallet = await users.user_data(call.from_user.id)
        username = call.from_user.username
        await call.bot.send_message(
            decouple.config("GROUP_ID"),
            f'Пользователь {"@" + username if username is not None else call.from_user.id} '
            f'отправил заявку на вывод средств:\n<b>Cумма:</b> {data.get("amount")}\n<b>Кошелёк TRC-20:</b> {wallet[6]}'
            f'\n\nПодробнее по ссылке: http://89.223.121.160:8000/admin/app/output/'
            f'\n\nИнструкция: 1. Подтвердите транзакцию и добавьте хэш транзакции!'
            f'\n2. Создайте успешный в вывод во вкладке "Истории пополнения и вывода" -> '
            f'\n3. Измените баланс юзера во вкладке "Коллективный аккаунт - Балансы" и '
            f'уберите Зарезервированный баланс (0,0)')
        await state.finish()
    else:
        text = 'Вы отменили операцию!'
        if language[4] == "EN":
            text = 'Operation canceled!'
        lol = await call.message.answer(text)
        await asyncio.sleep(2)
        await call.bot.delete_message(call.from_user.id, lol.message_id)
        await state.finish()
        await handlers.commands.bot_start_call(call)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(withdraw_main_menu, text='withdrawal')
    dp.register_callback_query_handler(withdrawal_handler, text='withdrawal_funds')
    dp.register_callback_query_handler(withdrawal_handler_collective, text="withdrawal_500")
    dp.register_callback_query_handler(withdrawal_handler_personal, text="withdrawal_15000")
    dp.register_callback_query_handler(change_wallet_new, text='change_wallet')
    dp.register_callback_query_handler(change_percentage, text='change_percentage')
    dp.register_callback_query_handler(change_percentage_step2, state=ChangePercentage.percentage)
    dp.register_message_handler(change_wallet_step2, state=ChangeWallet.wallet)
    dp.register_message_handler(handle_amount, state=NewWallet.amount)
    dp.register_callback_query_handler(finish_withdrawal, state=NewWallet.amount)
