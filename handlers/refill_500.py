import asyncio
import datetime
import decouple

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound
from database import users, balance, thedex_db, stabpool
from handlers.google import sheets_connection
from keyboards import inline
from binance import thedex


class SmallUser(StatesGroup):
    hold = State()
    amount = State()
    currency = State()
    finish = State()


async def registration_500(call: types.CallbackQuery):
    rows = await thedex_db.get_transaction(call.from_user.id)
    language = await users.user_data(call.from_user.id)
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    if not rows:
        text = await users.get_text('Пополнение (коллективный аккаунт)', language[4])
        dep_msg = await call.message.answer(text, reply_markup=inline.back_menu(language[4]))
        await SmallUser.amount.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data({"dep_msg": dep_msg.message_id})
    if len(rows) == 1:
        row = rows[0]
        await smalluser_check(call, row)
    if len(rows) > 1:
        text = await users.get_text('Ошибка пополнения #5', language[4])
        await call.message.answer(text)


async def deposit_500(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'from_500':
        text = await users.get_text('Пополнение (коллективный аккаунт)', language[4])
        dep_msg = await call.message.edit_text(text, reply_markup=inline.back_menu(language[4]))
        await SmallUser.amount.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data({"dep_msg": dep_msg.message_id})


async def back_menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    language = await users.user_data(call.from_user.id)
    text = 'Выберите один из вариантов:'
    if language[4] == "EN":
        text = 'Select at least one option:'
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.refill_account_2(language[4]))


async def smalluser_step1(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            await msg.bot.delete_message(chat_id=msg.from_id, message_id=data.get('dep_msg'))
            await msg.delete()
        except MessageToDeleteNotFound:
            pass
    language = await users.user_data(msg.from_user.id)
    if msg.text.isdigit():
        if 50 <= int(msg.text):
            summary = int(msg.text)
            response = await thedex.create_invoice(summary, msg.from_id, "Коллективный аккаунт")
            await state.update_data({'status': 500, 'amount': int(msg.text), 'invoiceId': response})
            await users.set_status(status="500", tg_id=msg.from_id)
            text = "🌐 Выберите сеть пополнения:"
            if language[4] == "EN":
                text = "🌐 Select deposit cryptocurrency:"
            await msg.answer(text, reply_markup=inline.return_currencies())
            await thedex_db.insert_transaction(msg.from_id, int(msg.text), response)
            await SmallUser.next()
        elif int(msg.text) < 50:
            text = await users.get_text('Ошибка пополнения #6', language[4])
            dep_msg = await msg.answer(text)
            await state.update_data({"dep_msg": dep_msg.message_id})
    else:
        text = await users.get_text('Ошибка пополнения #3', language[4])
        await msg.answer(text)


async def smalluser_step2(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    async with state.proxy() as data:
        data['currency'] = call.data
        crypto_dict = {
            'BTC_BITCOIN': 'Bitcoin',
            'ETH_ETHEREUM': 'Ethereum',
            'USDT_TRON': 'USDT TRC20',
            'USDT_ETHEREUM': 'USDT ERC20',
            'TRX_TRON': 'Tron',
            'LTC_LITECOIN': 'Litecoin',
            'BNB_BSC': 'Binance Coin',
            'BUSD_BSC': 'Binance USD'
        }
        currency_str = crypto_dict[data.get('currency')]
        language = await users.user_data(call.from_user.id)
        wallet = await thedex.pay_invoice(data.get('currency'), data.get('invoiceId'))
        count = wallet[1]
        if "." in count:
            count = count.replace(".", ",")
        text = f"Отправьте `{count}` {currency_str} на указанный адрес:\n\n`{wallet[0]}`\n\n" \
               f"Перед совершением транзакции внимательно проверьте адрес получателя и сумму перевода, оба значения " \
               f"должны совпадать со значениями в сообщении" \
               f"\n\n*Срок действия кошелька для пополнения \- 60 минут, " \
               f"если вы не успеваете пополнить за это время \- отмените транзакцию\!*"
        if language[4] == "EN":
            text = f"Please send {count} {currency_str} to the provided address:\n\n{wallet[0]}\n\n" \
                   f"Before making the transaction, carefully verify the recipient's address and the transfer amount." \
                   f" Both values should match the ones in the message. " \
                   f"\n\n*Wallet validity period for top-up is 60 minutes. If you are unable to complete the " \
                   f"top-up within this time frame, please cancel the transaction!*"
        await call.message.answer(text, reply_markup=inline.finish_transaction(language[4]),
                                  parse_mode=types.ParseMode.MARKDOWN_V2)
    await SmallUser.next()


async def smalluser_finish(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    async with state.proxy() as data:
        status, title = await thedex.invoice_one(data.get('invoiceId'))
    if status == "Waiting":
        text = await users.get_text('Статус Waiting (thedex)', language[4])
        await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))
    if status == "Unpaid":
        text = await users.get_text('Статус Unpaid (thedex)', language[4])
        await state.set_state(SmallUser.amount.state)
        await call.message.answer(text)
    if status == "Successful":
        text = await users.get_text('Статус Successful (thedex)', language[4])
        hold = await balance.get_hold(call.from_user.id)
        hold = hold[0] if hold is not None else None
        if not hold or hold < 30:
            await balance.update_hold(30, call.from_user.id)
        await balance.insert_deposit(call.from_user.id, data.get("amount"))
        await balance.insert_balance_history(
            call.from_user.id, data.get("amount"), data.get('invoiceId'), "Коллективный аккаунт")
        await thedex_db.insert_status(call.from_user.id, data.get('invoiceId'), status)
        await state.finish()
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
        user_name = "@"+call.from_user.username if call.from_user.username is not None else call.from_user.full_name
        await call.bot.send_message(decouple.config("GROUP_ID"),
                                    f'Пользователь {user_name} успешно пополнил коллективный аккаунт на '
                                    f'{data.get("amount")} USDT!'
                                    f'\n\n Подробнее: http://89.223.121.160:8000/admin/app/balance/')
        sh = await sheets_connection()
        worksheet_name = "Сумма пополнения пула"
        worksheet = sh.worksheet(worksheet_name)
        worksheet.append_row((datetime.datetime.now().date().strftime("%Y-%m-%d"),
                              call.from_user.id, "Пополнение", data.get("amount")))
    if status == "Rejected":
        text = await users.get_text('Статус Rejected (thedex)', language[4])
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
    else:
        text = await users.get_text('Статус Waiting (thedex)', language[4])
        await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))


async def smalluser_check(call: types.CallbackQuery, row):
    language = await users.user_data(call.from_user.id)
    status, title = await thedex.invoice_one(row[2])
    if status == "Waiting":
        text = await users.get_text('Статус Waiting (thedex)', language[4])
        await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))
    if status == "Unpaid":
        text = await users.get_text('Статус Unpaid у NFT', language[4])
        await call.message.answer(text)
        await thedex_db.insert_status(call.from_user.id, row[2], status)
        call.data = "500"
        await registration_500(call)
    if status == "Successful":
        text = await users.get_text('Статус Successful (thedex)', language[4])
        if title == "Стабилизационный пул":
            hold = await stabpool.get_hold(call.from_user.id)
            hold = hold[0] if hold is not None else None
            if not hold or hold < 90:
                await stabpool.update_hold(90, call.from_user.id)
            await stabpool.insert_deposit(call.from_user.id, row[1])
            await balance.insert_balance_history(call.from_user.id, row[1], row[2], "Стабилизационный пул")
            await thedex_db.insert_status(call.from_user.id, row[2], status)
            user_name = "@" + call.from_user.username if call.from_user.username is not None else call.from_user.full_name
            await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
            sh = await sheets_connection()
            worksheet_name = "Сумма пополнения пула"
            worksheet = sh.worksheet(worksheet_name)
            worksheet.append_row((datetime.datetime.now().date().strftime("%Y-%m-%d"),
                                  call.from_user.id, "Пополнение (стабпул)", row[1]))
            await call.bot.send_message(decouple.config("GROUP_ID"),
                                        f'Пользователь {user_name} успешно пополнил стабпул на '
                                        f'{row[1]} USDT!'
                                        f'\n\n Подробнее: http://89.223.121.160:8000/admin/app/stabpool/')

        else:
            hold = await balance.get_hold(call.from_user.id)
            hold = hold[0] if hold is not None else None
            if not hold or hold < 30:
                await balance.update_hold(30, call.from_user.id)
            await balance.insert_deposit(call.from_user.id, row[1])
            await balance.insert_balance_history(call.from_user.id, row[1], row[2], "Коллективный аккаунт")
            await thedex_db.insert_status(call.from_user.id, row[2], status)
            user_name = "@" + call.from_user.username if call.from_user.username is not None else call.from_user.full_name
            await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
            sh = await sheets_connection()
            worksheet_name = "Сумма пополнения пула"
            worksheet = sh.worksheet(worksheet_name)
            worksheet.append_row((datetime.datetime.now().date().strftime("%Y-%m-%d"),
                                  call.from_user.id, "Пополнение (коллективный акк)", row[1]))
            await call.bot.send_message(decouple.config("GROUP_ID"),
                                        f'Пользователь {user_name} успешно пополнил коллективный аккаунт на '
                                        f'{row[1]} USDT!'
                                        f'\n\n Подробнее: http://89.223.121.160:8000/admin/app/balance/')
    if status == "Rejected":
        text = await users.get_text('Статус Rejected (thedex)', language[4])
        await thedex_db.insert_status(call.from_user.id, row[2], status)
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))


async def smalluser_check_2(call: types.CallbackQuery):
    await call.message.delete()
    rows = await thedex_db.get_transaction(call.from_user.id)
    user_name = "@" + call.from_user.username if call.from_user.username is not None else call.from_user.full_name
    try:
        row = rows[0]
        language = await users.user_data(call.from_user.id)
        status, title = await thedex.invoice_one(row[2])
        if status == "Waiting":
            text = await users.get_text('Статус Waiting (thedex)', language[4])
            await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))
        if status == "Unpaid":
            text = await users.get_text('Статус Unpaid у NFT', language[4])
            await call.message.answer(text)
            await thedex_db.insert_status(call.from_user.id, row[2], status)
            call.data = "500"
            await registration_500(call)
        if status == "Successful":
            text = await users.get_text('Статус Successful (thedex)', language[4])
            if language[4] == "EN":
                text = "Payment was successful."
            if title == "Стабилизационный пул":
                hold = await stabpool.get_hold(call.from_user.id)
                hold = hold[0] if hold is not None else None
                if not hold or hold < 90:
                    await stabpool.update_hold(90, call.from_user.id)
                await stabpool.insert_deposit(call.from_user.id, row[1])
                await balance.insert_balance_history(call.from_user.id, row[1], row[2], "Стабилизационный пул")
                await thedex_db.insert_status(call.from_user.id, row[2], status)
                await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
                sh = await sheets_connection()
                worksheet_name = "Сумма пополнения пула"
                worksheet = sh.worksheet(worksheet_name)
                worksheet.append_row((datetime.datetime.now().date().strftime("%Y-%m-%d"),
                                      call.from_user.id, "Пополнение (стабпул)", row[1]))
                await call.bot.send_message(decouple.config("GROUP_ID"),
                                            f'Пользователь {user_name} успешно пополнил стабпул на '
                                            f'{row[1]} USDT!'
                                            f'\n\n Подробнее: http://89.223.121.160:8000/admin/app/stabpool/')

            else:
                hold = await balance.get_hold(call.from_user.id)
                hold = hold[0] if hold is not None else None
                if not hold or hold < 30:
                    await balance.update_hold(30, call.from_user.id)
                await balance.insert_deposit(call.from_user.id, row[1])
                await balance.insert_balance_history(call.from_user.id, row[1], row[2], "Коллективный аккаунт")
                await thedex_db.insert_status(call.from_user.id, row[2], status)
                await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
                sh = await sheets_connection()
                worksheet_name = "Сумма пополнения пула"
                worksheet = sh.worksheet(worksheet_name)
                worksheet.append_row((datetime.datetime.now().date().strftime("%Y-%m-%d"),
                                      call.from_user.id, "Пополнение (коллективный акк)", row[1]))
                await call.bot.send_message(decouple.config("GROUP_ID"),
                                            f'Пользователь {user_name} успешно пополнил коллективный аккаунт на '
                                            f'{row[1]} USDT!'
                                            f'\n\n Подробнее: http://89.223.121.160:8000/admin/app/balance/')
        if status == "Rejected":
            text = await users.get_text('Статус Rejected (thedex)', language[4])
            await thedex_db.insert_status(call.from_user.id, row[2], status)
            await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
    except IndexError:
        language = await users.user_data(call.from_user.id)
        text = await users.get_text('Ошибка отмены транзакции', language[4])
        message = await call.message.answer(text)
        await asyncio.sleep(5)
        await call.bot.delete_message(call.message.chat.id, message.message_id)


async def transaction_detail(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    rows = await thedex_db.get_transaction(call.from_user.id)
    try:
        row = rows[0]
        status = await thedex.invoice_one_2(row[2])
        count = status[3]
        try:
            if "." in count:
                count = count.replace(".", ",")
            text = f"<b>Аккаунт пополнения:</b>: {status[4]}\n\n" \
                   f"<b>Сумма к оплате:</b><em> {count} {status[2]} </em>\n" \
                   f"<b>Статус оплаты:</b><em> {status[0]}</em>\n" \
                   f"<b>Кошелек для оплаты:</b><em> {status[1]}</em>\n"
            if language[4] == "EN":
                text = f"<b>Account type</b>: {status[4]}\n\n" \
                       f"<b>Payment amount:</b><em> {count} {status[2]} </em>\n" \
                       f"<b>Payment status:</b><em> {status[0]}</em>\n" \
                       f"<b>Payment wallet:</b><em> {status[1]}</em>\n"
            await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))
        except TypeError:
            text = await users.get_text('Ошибка транзакции', language[4])
            await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
            await thedex_db.delete_transaction(row[0])
    except IndexError:
        language = await users.user_data(call.from_user.id)
        text = await users.get_text('Ошибка отмены транзакции', language[4])
        message = await call.message.answer(text)
        await asyncio.sleep(5)
        await call.bot.delete_message(call.message.chat.id, message.message_id)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(registration_500, text='500')
    dp.register_callback_query_handler(deposit_500, lambda c: c.data in ['from_500', 'from_1000'])
    dp.register_callback_query_handler(transaction_detail, text="transaction_detail", state="*")
    dp.register_message_handler(smalluser_step1, state=SmallUser.amount)
    dp.register_callback_query_handler(back_menu, state=SmallUser.amount)
    dp.register_callback_query_handler(smalluser_step2, state=SmallUser.currency)
    dp.register_callback_query_handler(smalluser_finish, state=SmallUser.finish)
    dp.register_callback_query_handler(smalluser_check_2, text="transaction_status")
