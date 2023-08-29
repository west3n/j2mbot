import handlers.refill

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound

from database import users, thedex_db
from demo import dm_inline, dm_database
from handlers.refill_500 import smalluser_check
from keyboards import inline
from binance import thedex


class DemoStabPoolUser(StatesGroup):
    hold = State()
    amount = State()
    currency = State()
    finish = State()


async def registration_500(call: types.CallbackQuery):
    rows = await thedex_db.get_transaction(call.from_user.id)
    language = await users.user_data(call.from_user.id)
    await dm_database.get_balance_stabpool(call.from_user.id)
    sum_refill = 0
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
            dep_msg = await call.message.answer(text, reply_markup=dm_inline.back_menu(language[4]))
            await DemoStabPoolUser.amount.set()
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
    await call.message.answer(text, reply_markup=dm_inline.dm_refill_account_2(language[4]))


async def smalluser_step1(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            await msg.bot.delete_message(chat_id=msg.from_id,
                                         message_id=data.get('dep_msg'))
            await msg.delete()
        except MessageToDeleteNotFound:
            pass
    language = await users.user_data(msg.from_user.id)
    sum_refill = 0
    if msg.text.isdigit():
        if 1000 <= int(msg.text) <= (20000 - sum_refill):
            summary = int(msg.text)
            response = await thedex.create_invoice(summary, msg.from_id, "[DEMO] Стабилизационный пул")
            await state.update_data({'status': 500, 'amount': int(msg.text), 'invoiceId': response})
            text = await users.get_text("Выбор сети пополнения", language[4])
            await msg.answer(text, reply_markup=inline.return_currencies())
            await DemoStabPoolUser.next()
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
    await DemoStabPoolUser.next()


async def smalluser_finish(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    async with state.proxy() as data:
        text = await users.get_text("Статус Successful (thedex)", language[4])
        await dm_database.insert_deposit(call.from_user.id, data.get("amount"))
        await dm_database.insert_demo_balance_history(
            call.from_user.id, data.get("amount"), "IN", data.get('invoiceId'))
        await state.finish()
        await call.message.answer(text, reply_markup=await dm_inline.dm_main_menu(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(registration_500, text='dm_stabpool')
    dp.register_message_handler(smalluser_step1, state=DemoStabPoolUser.amount)
    dp.register_callback_query_handler(back_menu, state=DemoStabPoolUser.amount)
    dp.register_callback_query_handler(smalluser_step2, state=DemoStabPoolUser.currency)
    dp.register_callback_query_handler(smalluser_finish, state=DemoStabPoolUser.finish)
