import datetime
import decouple
import handlers.refill

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound

from database import users, balance, thedex_db, stabpool
from handlers.google import sheets_connection
from handlers.refill_500 import smalluser_check
from keyboards import inline
from binance import thedex


class StabPoolUser(StatesGroup):
    hold = State()
    amount = State()
    currency = State()
    finish = State()


async def registration_500(call: types.CallbackQuery):
    rows = await thedex_db.get_transaction(call.from_user.id)
    language = await users.user_data(call.from_user.id)
    await stabpool.get_balance(call.from_user.id)
    sum_refill = await balance.get_stabpool_refill_sum(call.from_user.id)
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    if not rows:
        if sum_refill >= 20000:
            text = await users.get_text("Стабпул ошибка #1", language[4])
            await call.answer(text, show_alert=True)
            await handlers.refill.handle_deposit_funds(call)
        else:
            text = await users.get_text("Стабпул пополнение", language[4])
            text = text.replace('{сумма}', f'{20000 - sum_refill}')
            dep_msg = await call.message.answer(text, reply_markup=inline.back_menu(language[4]))
            await StabPoolUser.amount.set()
            state = Dispatcher.get_current().current_state()
            await state.update_data({"dep_msg": dep_msg.message_id})
    if len(rows) == 1:
        row = rows[0]
        await smalluser_check(call, row)
    if len(rows) > 1:
        text = await users.get_text("Ошибка пополнения #5", language[4])
        await call.message.answer(text)


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
            await msg.bot.delete_message(chat_id=msg.from_id,
                                         message_id=data.get('dep_msg'))
            await msg.delete()
        except MessageToDeleteNotFound:
            pass
    language = await users.user_data(msg.from_user.id)
    sum_refill = await balance.get_stabpool_refill_sum(msg.from_user.id)
    if msg.text.isdigit():
        if 1000 <= int(msg.text) <= (20000-sum_refill):
            summary = int(msg.text)
            response = await thedex.create_invoice(summary, msg.from_id, "Стабилизационный пул")
            await state.update_data({'status': 500, 'amount': int(msg.text), 'invoiceId': response})
            await users.set_status(status="500", tg_id=msg.from_id)
            text = await users.get_text("Выбор сети пополнения", language[4])
            await msg.answer(text, reply_markup=inline.return_currencies())
            await thedex_db.insert_transaction(msg.from_id, int(msg.text), response)
            await StabPoolUser.next()
        elif int(msg.text) > 20000:
            text = await users.get_text("Стабпул ошибка #2", language[4])
            text = text.replace('{сумма}', f'{20000 - sum_refill}')
            dep_msg = await msg.answer(text)
            await state.update_data({"dep_msg": dep_msg.message_id})
        elif int(msg.text) < 1000:
            text = await users.get_text("Стабпул ошибка #3", language[4])
            dep_msg = await msg.answer(text)
            await state.update_data({"dep_msg": dep_msg.message_id})
    else:
        text = await users.get_text("Ошибка пополнения #3", language[4])
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
               f"если вы не успеваете пополнить за это время отмените транзакцию\!*"
        if language[4] == "EN":
            text = f"Please send {count} {currency_str} to the provided address:\n\n{wallet[0]}\n\n" \
                   f"Before making the transaction, carefully verify the recipient's address and the transfer amount." \
                   f" Both values should match the ones in the message."
        await call.message.answer(text, reply_markup=inline.finish_transaction(language[4]),
                                  parse_mode=types.ParseMode.MARKDOWN_V2)
    await StabPoolUser.next()


async def smalluser_finish(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    async with state.proxy() as data:
        status, title = await thedex.invoice_one(data.get('invoiceId'))
    if status == "Waiting":
        text = await users.get_text("Статус Waiting (thedex)", language[4])
        await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))
    elif status == "Unpaid":
        text = await users.get_text("Статус Unpaid (thedex) (стабпул)", language[4])
        await state.set_state(StabPoolUser.amount.state)
        await call.message.answer(text)
    elif status == "Successful":
        text = await users.get_text("Статус Successful (thedex)", language[4])
        hold = await stabpool.get_hold(call.from_user.id)
        hold = hold[0] if hold is not None else None
        if not hold or hold < 90:
            await stabpool.update_hold(90, call.from_user.id)
        await stabpool.insert_deposit(call.from_user.id, data.get("amount"))
        await balance.insert_balance_history(call.from_user.id, data.get("amount"), data.get('invoiceId'),
                                             "Стабилизационный пул")
        await thedex_db.insert_status(call.from_user.id, data.get('invoiceId'), status)
        await state.finish()
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
        user_name = "@" + call.from_user.username if call.from_user.username is not None else call.from_user.full_name
        await call.bot.send_message(decouple.config("GROUP_ID"),
                                    f'Пользователь {user_name} успешно пополнил стабпул на '
                                    f'{data.get("amount")} USDT!'
                                    f'\n\n Подробнее: http://89.223.121.160:8000/admin/app/balance/')
        sh = await sheets_connection()
        worksheet_name = "Сумма пополнения пула"
        worksheet = sh.worksheet(worksheet_name)
        worksheet.append_row((datetime.datetime.now().date().strftime("%d.%m.%Y"),
                              call.from_user.id, "Пополнение", data.get("amount")))
    elif status == "Rejected":
        text = await users.get_text("Статус Rejected (thedex)", language[4])
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
    else:
        text = await users.get_text("Статус Waiting (thedex)", language[4])
        await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(registration_500, text='stabpool')
    dp.register_message_handler(smalluser_step1, state=StabPoolUser.amount)
    dp.register_callback_query_handler(back_menu, state=StabPoolUser.amount)
    dp.register_callback_query_handler(smalluser_step2, state=StabPoolUser.currency)
    dp.register_callback_query_handler(smalluser_finish, state=StabPoolUser.finish)
