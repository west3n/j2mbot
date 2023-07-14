import datetime
import decouple
from aiogram.utils.exceptions import MessageToDeleteNotFound

import handlers.commands

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import inline
from database import users, balance, output


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
    text = "Пришлите новый адрес криптокошелька TRC-20 для вывода:"
    if language[4] == 'EN':
        text = "Please provide a new cryptocurrency wallet TRC-20 address for withdrawal:"
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
    text = "Выберите процент, который вы хотите реинвестировать после каждой торговой недели:\n\n" \
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
    text = 'Вывод средств пока не доступен, функция находится в разработке!\n\n' \
           'Доступ откроется в ближайшем обновлении 18.07.2023'
    language = await users.user_data(call.from_user.id)
    if language[4] == "EN":
        text = "Withdrawal not available, function is under development!" \
               "\n\nAccess will be taken in nearest update in 18.07.2023"
    await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
    # withdrawal_balance = await balance.get_my_balance(call.from_user.id)
    # withdrawal_balance = withdrawal_balance if withdrawal_balance is not None else 0
    # wallet = await users.user_data(call.from_user.id)
    # first_trans = await balance.get_first_transaction(call.from_user.id)
    # date_first = first_trans[2]
    # status = await users.check_status(call.from_user.id)
    # hold = await balance.get_hold(call.from_user.id)
    # bal_user, deposit, withdraw = await balance.get_balance(call.from_user.id)
    # try:
    #     hold = hold[0]
    # except TypeError:
    #     hold = None
    # try:
    #     status = status[0]
    # except TypeError:
    #     status = None
    # if status:
    #     if status == "1000":
    #         if first_trans:
    #             now = datetime.datetime.now()
    #             if now.tzinfo is None:
    #                 now = now.replace(tzinfo=datetime.timezone.utc)
    #             if hold:
    #                 if date_first + datetime.timedelta(days=int(hold)) <= now:
    #                     difference = date_first - now
    #                     if difference.total_seconds() >= 14 * 24 * 60 * 60:
    #                         text = f"Первое пополнение было выполнено {date_first}\n\n" \
    #                                f"Доступная дата вывода: {date_first + datetime.timedelta(days=14)}"
    #                         if language[4] == 'EN':
    #                             text = f"The first top-up was made on {date_first}\n\n"
    #                             f"Available withdrawal date: {date_first + datetime.timedelta(days=14)}"
    #                         await call.message.delete()
    #                         await call.message.answer(text, reply_markup=inline.main_withdraw(language[4]))
    #                     elif not wallet[6]:
    #                         text = "Для того, чтобы вывести средства, нужно добавить адрес кошелька для вывода.\n" \
    #                                "Ответным сообщением пришлите адрес кошелька <b>TRC-20 USDT</b>\n\n" \
    #                                "Вы всегда сможете изменить его в меню 'Вывод'."
    #                         if language[4] == 'EN':
    #                             text = "To withdraw funds, you need to add a withdrawal wallet address.\n\n"
    #                             "You can always change it in the 'Withdrawal' section."
    #
    #                         await call.message.answer(text)
    #                         await NewWallet.wallet.set()
    #                     elif withdrawal_balance == 0:
    #                         await state.set_state(NewWallet.amount.state)
    #                         text = f"<b>Баланс, доступный к выводу:</b> " \
    #                                f"{withdrawal_balance if withdrawal_balance is not None else 0} USDT"
    #                         if language[4] == 'EN':
    #                             text = f"<b>The balance available for withdrawal:</b> " \
    #                                    f"{withdrawal_balance if withdrawal_balance is not None else 0} USDT"
    #
    #                         await state.finish()
    #                         await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
    #                     else:
    #                         text = f"Баланс, доступный к выводу: {withdrawal_balance} USDT" \
    #                                f"\nCумма минимального вывода 50 USDT" \
    #                                f"\n\nНапишите сумму USDT, которую хотите вывести:"
    #                         if language[4] == 'EN':
    #                             text = f"The balance available for withdrawal: {withdrawal_balance} USDT" \
    #                                    f"\nMinimum withdrawal amount is 50 USDT." \
    #                                    f"\n\nPlease write the amount of USDT you want to withdraw:"
    #
    #                         await call.message.answer(text)
    #                         await state.set_state(NewWallet.amount.state)
    #                 else:
    #                     if not wallet[6]:
    #                         text = "Для того, чтобы вывести средства, нужно добавить адрес кошелька для вывода.\n" \
    #                                "Ответным сообщением пришлите адрес кошелька <b>TRC-20 USDT</b>\n\n" \
    #                                "Вы всегда сможете изменить его в меню 'Вывод'."
    #                         if language[4] == 'EN':
    #                             text = "To withdraw funds, you need to add a withdrawal wallet address.\n\n"
    #                             "You can always change it in the 'Withdrawal' section."
    #
    #                         await call.message.answer(text)
    #                         await NewWallet.wallet.set()
    #                     else:
    #                         text = f"<b>Баланс, доступный к выводу:</b> {withdrawal_balance if withdrawal_balance is not None else 0} USDT\n\n" \
    #                                f"Ближайшая дата возможного вывода: {date_first + datetime.timedelta(days=int(hold))}"
    #                         if language[4] == 'EN':
    #                             text = f"<b>The balance available for withdrawal:</b> " \
    #                                    f"{withdrawal_balance if withdrawal_balance is not None else 0} USDT"
    #
    #                         await state.finish()
    #                         await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
    #             else:
    #                 text = f"Ваш суммарный баланс:{int(withdrawal_balance) + deposit} USDT" \
    #                        f"Доступные активы к выводу: {withdrawal_balance} USDT" \
    #                        f"Заявки на вывод, ожидающие обработки: {withdraw}" \
    #                        f"Минимальная сумма вывода: 50 USDT" \
    #                        f"Ближайшая дата доступная к выводу: {date_first + datetime.timedelta(days=int(hold))}" \
    #                        f"Ваш номер кошелька для вывода: {wallet[6]}" \
    #                        f"Если это верный номер кошелька, подтвердите вывод на него." \
    #                        f"Если Нужно вывести активы на другой кошелек, измените его адрес."
    #                 if language[4] == 'EN':
    #                     text = f"<b>The balance available for withdrawal:</b> " \
    #                            f"{withdrawal_balance if withdrawal_balance is not None else 0} USDT"
    #
    #                 await state.finish()
    #                 await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
    #     elif status == "500":
    #         if first_trans:
    #             now = datetime.datetime.now()
    #             if now.tzinfo is None:
    #                 now = now.replace(tzinfo=datetime.timezone.utc)
    #             date_first = first_trans[2]
    #             withdrawal_balance = withdrawal_balance if withdrawal_balance is not None else 0
    #             if withdrawal_balance > 1000:
    #                     difference = date_first - now
    #                     if difference.total_seconds() >= 14 * 24 * 60 * 60:
    #                         text = f"Первое пополнение было выполнено {date_first}\n\n" \
    #                                f"Доступная дата вывода: {date_first + datetime.timedelta(days=14)}"
    #                         if language[4] == 'EN':
    #                             text = f"The first top-up was made on {date_first}\n\n"
    #                             f"Available withdrawal date: {date_first + datetime.timedelta(days=14)}"
    #                         await call.message.delete()
    #                         await call.message.answer(text, reply_markup=inline.main_withdraw(language[4]))
    #                     elif not wallet[6]:
    #                         text = "Для того, чтобы вывести средства, нужно добавить адрес кошелька для вывода.\n" \
    #                                "Ответным сообщением пришлите адрес кошелька <b>TRC-20 USDT</b>\n\n" \
    #                                "Вы всегда сможете изменить его в меню 'Вывод'."
    #                         if language[4] == 'EN':
    #                             text = "To withdraw funds, you need to add a withdrawal wallet address.\n\n"
    #                             "You can always change it in the 'Withdrawal' section."
    #
    #                         await call.message.answer(text)
    #                         await NewWallet.wallet.set()
    #                     elif withdrawal_balance is None or 0:
    #                         await state.set_state(NewWallet.amount.state)
    #                         text = f"<b>Баланс, доступный к выводу:</b> " \
    #                                f"{withdrawal_balance if withdrawal_balance is not None else 0} USDT"
    #                         if language[4] == 'EN':
    #                             text = f"<b>The balance available for withdrawal:</b> " \
    #                                    f"{withdrawal_balance if withdrawal_balance is not None else 0} USDT"
    #
    #                         await state.finish()
    #                         await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
    #                     else:
    #                         text = f"Баланс, доступный к выводу: {withdrawal_balance} USDT" \
    #                                f"\nCумма минимального вывода 50 USDT" \
    #                                f"\n\nНапишите сумму USDT, которую хотите вывести:"
    #                         if language[4] == 'EN':
    #                             text = f"The balance available for withdrawal: {withdrawal_balance} USDT" \
    #                                    f"\nMinimum withdrawal amount is 50 USDT." \
    #                                    f"\n\nPlease write the amount of USDT you want to withdraw:"
    #
    #                         await call.message.answer(text)
    #                         await state.set_state(NewWallet.amount.state)
    #             else:
    #                 if not wallet[6]:
    #                     text = "Для того, чтобы вывести средства, нужно добавить адрес кошелька для вывода.\n" \
    #                            "Ответным сообщением пришлите адрес кошелька <b>TRC-20 USDT</b>\n\n" \
    #                            "Вы всегда сможете изменить его в меню 'Вывод'."
    #                     if language[4] == 'EN':
    #                         text = "To withdraw funds, you need to add a withdrawal wallet address.\n\n"
    #                         "You can always change it in the 'Withdrawal' section."
    #
    #                     await call.message.answer(text)
    #                     await NewWallet.wallet.set()
    #                 else:
    #                     text = f"Вывод для вашего статуса доступен при балансе более 1000 USDT"
    #                     if language[4] == 'EN':
    #                         text = f"Withdrawal is available for your status with a balance of over 1000 USDT."
    #
    #                     await state.finish()
    #                     await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
    #
    # else:
    #     text = f"Ваш суммарный баланс:{int(withdrawal_balance) + deposit } USDT" \
    #            f"Доступные активы к выводу: {withdrawal_balance} USDT" \
    #            f"Заявки на вывод, ожидающие обработки: {withdraw}" \
    #            f"Минимальная сумма вывода: 50 USDT" \
    #            f"Ближайшая дата доступная к выводу: {date_first + datetime.timedelta(days=int(hold))}" \
    #            f"Ваш номер кошелька для вывода: {wallet[6]}" \
    #            f"Если это верный номер кошелька, подтвердите вывод на него." \
    #            f"Если Нужно вывести активы на другой кошелек, измените его адрес."
    #     if language[4] == 'EN':
    #         text = f"<b>The balance available for withdrawal:</b> " \
    #                f"{withdrawal_balance if withdrawal_balance is not None else 0} USDT"
    #
    #     await state.finish()
    #     await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))


async def handle_amount(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    if not msg.text.isdigit():
        text = 'Пожалуйста, используйте только цифры!'
        if language[4] == 'EN':
            text = 'Please, use digits only!'
        await msg.delete()
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
    if call.data == 'confirm_withdrawal':
        await call.message.delete()
        await call.bot.send_chat_action(call.message.chat.id, 'typing')
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
        await call.message.edit_text(text)
        await handlers.commands.bot_start_call(call)
        await state.finish()

def register(dp: Dispatcher):
    dp.register_callback_query_handler(withdraw_main_menu, text='withdrawal')
    dp.register_callback_query_handler(withdrawal_handler, text='withdrawal_funds')
    dp.register_callback_query_handler(change_wallet_new, text='change_wallet')
    dp.register_callback_query_handler(change_percentage, text='change_percentage')
    dp.register_callback_query_handler(change_percentage_step2, state=ChangePercentage.percentage)
    dp.register_message_handler(change_wallet_step2, state=ChangeWallet.wallet)
    dp.register_message_handler(handle_amount, state=NewWallet.amount)
    dp.register_callback_query_handler(finish_withdrawal, state=NewWallet.amount)
