from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound

from database import users, balance, thedex_db
from keyboards import inline
from binance import thedex
from demo import dm_inline, dm_database


class DemoSmallUser(StatesGroup):
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
        text = "<b>🆙 Введите сумму пополнения в USDT цифрами сообщением!</b>" \
               "\n\n💵 Минимальная сумма - <b>500 USDT</b>" \
               "\n\n<em>При пополнении Вы также оплачиваете стоимость AML проверки. " \
               "Сумма комиссии рассчитывается в зависимости от сети пополнения.</em>"
        if language[4] == 'EN':
            text = "🆙 Enter the replenishment amount in USDT using digits.\n\n" \
                   "💵Minimum amount - 500 USDT" \
                   "\n\nWhen making a deposit, you also cover the cost of AML verification. " \
                   "The commission amount is calculated based on the network used for the deposit."
        dep_msg = await call.message.answer(text, reply_markup=dm_inline.back_menu(language[4]))
        await DemoSmallUser.amount.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data({"dep_msg": dep_msg.message_id})
    else:
        text = "У вас несколько незакрытых транзакций, пожалуйста, напишите в " \
               "поддержку для решения вашей проблемы!"
        await call.message.answer(text)


async def deposit_500(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'dm_from_500':
        text = "<b>🆙 Введите сумму пополнения в USDT цифрами сообщением!</b>" \
               "\n\n💵 Минимальная сумма - <b>500 USDT</b>" \
               "\n\n<em>При пополнении Вы также оплачиваете стоимость AML проверки. " \
               "Сумма комиссии рассчитывается в зависимости от сети пополнения.</em>"
        if language[4] == 'EN':
            text = "🆙 Enter the replenishment amount in USDT using digits.\n\n" \
                   "💵Minimum amount - 500 USDT" \
                   "\n\nWhen making a deposit, you also cover the cost of AML verification. " \
                   "The commission amount is calculated based on the network used for the deposit."
        dep_msg = await call.message.edit_text(text, reply_markup=dm_inline.back_menu(language[4]))
        await DemoSmallUser.amount.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data({"dep_msg": dep_msg.message_id})


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
    if msg.text.isdigit():
        if 500 <= int(msg.text) < 1000:
            summary = int(msg.text)
            response = await thedex.create_invoice(summary, msg.from_id, "ДЕМО")
            await state.update_data({'status': 500, 'amount': int(msg.text), 'invoiceId': response})
            await users.set_status(status="500", tg_id=msg.from_id)
            text = "🌐 Выберите сеть пополнения:"
            if language[4] == "EN":
                text = "🌐 Select deposit cryptocurrency:"
            await msg.answer(text, reply_markup=inline.return_currencies())
            await thedex_db.insert_transaction(msg.from_id, int(msg.text), response)
            await DemoSmallUser.next()
        elif int(msg.text) >= 1000:
            summary = int(msg.text)
            response = await thedex.create_invoice(summary, msg.from_id, "ДЕМО")
            await state.update_data({'status': 1000, 'amount': int(msg.text), 'invoiceId': response})
            await thedex_db.insert_transaction(msg.from_id, int(msg.text), response)
            await users.set_status(status="1000", tg_id=msg.from_id)
            text = "⏳ Выберите длительность холда:"
            if language[4] == "EN":
                text = "⏳ Select hold time:"
            await msg.answer(text, reply_markup=inline.hold_kb(language[4]))
            await state.set_state(DemoSmallUser.hold.state)
        elif int(msg.text) < 500:
            text = "Сумма пополнения должна быть не менее 500 USDT, введите сумму пополнения еще раз!"
            if language[4] == "EN":
                text = "The deposit amount must be at least 500 USDT, please enter the deposit amount again!"
            dep_msg = await msg.answer(text)
            await state.update_data({"dep_msg": dep_msg.message_id})
    else:
        text = "Введите желаемую сумму пополнения числом, без запятых, букв и прочего!"
        if language[4] == "EN":
            text = "Please enter the desired deposit amount as a number, without commas, letters, or other symbols!"
        await msg.answer(text)


async def smalluser_hold(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    async with state.proxy() as data:
        data['hold'] = int(call.data)
        await balance.update_hold(int(call.data), call.from_user.id)
        text = "🌐 Выберите сеть пополнения:"
        if language[4] == "EN":
            text = "🌐 Select deposit cryptocurrency:"
        await call.message.answer(text, reply_markup=dm_inline.return_currencies())
        await state.set_state(DemoSmallUser.currency.state)


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
        text = f"DEMO\!\n\nОтправьте `{count}` {currency_str} на указанный адрес:\n\n`{wallet[0]}`\n\n" \
               f"Перед совершением транзакции внимательно проверьте адрес получателя и сумму перевода, оба значения " \
               f"должны совпадать со значениями в сообщении" \
               f"\n\n*Срок действия кошелька для пополнения \- 60 минут, " \
               f"если вы не успеваете пополнить за это время отмените транзакцию\!*"

        if language[4] == "EN":
            text = f"Please send {count} {currency_str} to the provided address:\n\n{wallet[0]}\n\n" \
                   f"Before making the transaction, carefully verify the recipient's address and the transfer amount." \
                   f" Both values should match the ones in the message."
        await call.message.answer(text, reply_markup=dm_inline.finish_transaction(language[4]),
                                  parse_mode=types.ParseMode.MARKDOWN_V2)
    await DemoSmallUser.next()


async def smalluser_finish(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = await users.user_data(call.from_user.id)
        if call.data == "dm_finish_payment":
            await call.message.delete()
            text = "🥳 Оплата прошла успешно! " \
                   "\n\n<em>Успешную транзакцию вы сможете увидеть в Балансе -> История пополнений</em>"
            if language[4] == "EN":
                text = "🥳 Payment was successful! " \
                       "\n\n<em>You can see the successful transaction in Balance -> Deposit History</em>"
            await dm_database.insert_demo_collective_balance(call.from_user.id, data.get("amount"))
            await dm_database.insert_demo_balance_history(call.from_user.id, data.get("amount"), "IN",
                                                          data.get("invoiceId"))
            await thedex_db.insert_status(call.from_user.id, data.get('invoiceId'), "ДЕМО")
            await state.finish()
            await call.message.answer(text, reply_markup=await dm_inline.dm_main_menu(language[4]))
        else:
            text = 'Вы отменили операцию по пополнению!'
            if language[4] == 'EN':
                text = 'Operation has been cancelled!'
            await thedex_db.delete_transaction_by_invoice_id(data.get("invoiceId"))
            await state.finish()
            await call.message.edit_text(text, reply_markup=await dm_inline.dm_main_menu(language[4]))


async def smalluser_check(call: types.CallbackQuery, row):
    language = await users.user_data(call.from_user.id)
    text = "🥳 Оплата прошла успешно! " \
           "\n\n<em>Успешную транзакцию вы сможете увидеть в Балансе -> История пополнений</em>"
    if language[4] == "EN":
        text = "🥳 Payment was successful! " \
               "\n\n<em>You can see the successful transaction in Balance -> Deposit History</em>"

    await dm_database.insert_demo_collective_balance(call.from_user.id, row[1])
    await dm_database.insert_demo_balance_history(call.from_user.id, row[2], "IN", row[1])
    await thedex_db.insert_status(call.from_user.id, row[2], "ДЕМО")
    await call.message.answer(text, reply_markup=await dm_inline.dm_main_menu(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(registration_500, text='dm_500')
    dp.register_callback_query_handler(deposit_500, lambda c: c.data in ['dm_from_500', 'dm_from_1000'])
    dp.register_message_handler(smalluser_step1, state=DemoSmallUser.amount)
    dp.register_callback_query_handler(back_menu, state=DemoSmallUser.amount)
    dp.register_callback_query_handler(smalluser_hold, state=DemoSmallUser.hold)
    dp.register_callback_query_handler(smalluser_step2, state=DemoSmallUser.currency)
    dp.register_callback_query_handler(smalluser_finish, state=DemoSmallUser.finish)
