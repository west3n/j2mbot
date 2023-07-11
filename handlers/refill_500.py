from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from database import users, balance, thedex_db
from keyboards import inline
from binance import thedex


class SmallUser(StatesGroup):
    amount_1000 = State()
    hold = State()
    amount = State()
    currency = State()
    finish = State()


async def registration_500(call: types.CallbackQuery):
    rows = await thedex_db.get_transaction(call.from_user.id)
    language = await users.user_data(call.from_user.id)
    try:
        await call.message.delete()
    except:
        pass
    if not rows:
        status = await users.check_status(call.from_user.id)
        try:
            status = status[0]
        except:
            status = None
        if status == "500":
            # await call.message.delete()
            text = "Введите сумму пополнения в USDT цифрами.\n" \
                   "Минимальная сумма - 500 USDT\n" \
                   "Максимальная сумма 999 USDT\n" \
                   "\n\nПри пополнении Вы также оплачиваете стоимость AML проверки. " \
                   "Сумма комиссии рассчитывается в зависимости от сети пополнения."
            if language[4] == 'EN':
                text = "Enter the replenishment amount in USDT using digits.\n" \
                       "Minimum amount - 500 USDT\n" \
                       "Maximum amount - 999 USDT\n" \
                       "\n\nWhen making a deposit, you also cover the cost of AML verification. " \
                       "The commission amount is calculated based on the network used for the deposit."
            await call.message.answer(text)
            await SmallUser.amount.set()
        elif status == "1000":
            # await call.message.delete()
            text = "Введите сумму пополнения в USDT цифрами\n." \
                   "Минимальная сумма - 1000 USDT\n" \
                   "\n\nПри пополнении Вы также оплачиваете стоимость AML проверки в размере. " \
                   "Сумма комиссии рассчитывается в зависимости от сети пополнения."
            if language[4] == 'EN':
                text = "Enter the replenishment amount in USDT using digits.\n" \
                       "Minimum amount - 1000 USDT\n" \
                       "\n\nWhen making a deposit, you also cover the cost of AML verification. " \
                       "The commission amount is calculated based on the network used for the deposit."
            await call.message.answer(text)
            await SmallUser.amount_1000.set()
        else:
            text = 'Какую сумму Вы хотите разместить?\n\n' \
                   'Нажмите кнопку ниже, чтобы выбрать тот вариант, который вам подходит.'
            if language[4] == 'EN':
                text = 'What amount would you like to place?\n\n' \
                       'Click the button below to select the option that suits you.'
            await call.message.answer(text, reply_markup=inline.refill_500_choice(language[4]))
    if len(rows) == 1:
        row = rows[0]
        await smalluser_check(call, row)
    if len(rows) > 1:
        text = "У вас несколько незакрытых транзакций, пожалуйста напишите в поддержку, для решения вашей проблемы!"
        await call.message.answer(text)


async def deposit_500(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'from_500':
        text = "Введите сумму пополнения в USDT цифрами.\n" \
               "Минимальная сумма - 500 USDT\n" \
               "Максимальная сумма 999 USDT\n" \
               "При пополнении Вы также оплачиваете стоимость AML проверки в размере 0,5% от суммы пополнения"
        if language[4] == 'EN':
            text = "Enter the replenishment amount in USDT using digits.\n"
            "Minimum amount - 500 USDT\n"
            "Maximum amount - 999 USDT\n"
            "When replenishing, you also pay for the cost of AML verification, which is 0.5% of the replenishment " \
            "amount."
        await call.message.edit_text(text)
        await SmallUser.amount.set()
    elif call.data == 'from_1000':
        text = "Введите сумму пополнения в USDT цифрами\n." \
               "Минимальная сумма - 1000 USDT\n" \
               "При пополнении Вы также оплачиваете стоимость AML проверки в размере 0,5% от суммы пополнения"
        if language[4] == 'EN':
            text = "Enter the replenishment amount in USDT using digits.\n"
            "Minimum amount - 1000 USDT\n"
            "When replenishing, you also pay for the cost of AML verification, which is 0.5% of the replenishment " \
            "amount."
        await call.message.edit_text(text)
        await SmallUser.amount_1000.set()


async def smalluser_step1(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    if msg.text.isdigit():
        if 500 <= int(msg.text) < 1000:
            async with state.proxy() as data:
                summary = int(msg.text)
                response = await thedex.create_invoice(summary, msg.from_id, "Пополнение больше 500")
                await state.update_data({'status': 500, 'amount': int(msg.text), 'invoiceId': response})
                await users.set_status(status="500", tg_id=msg.from_id)
                text = "Выберите сеть пополнения:"
                if language[4] == "EN":
                    text = "Select deposit cryptocurrency:"
                await msg.answer(text, reply_markup=inline.return_currencies())
                await thedex_db.insert_transaction(msg.from_id, int(msg.text), response)
                await SmallUser.next()
        else:
            text = "Сумма пополнения должна быть от 500 до 1000 USDT!"
            if language[4] == "EN":
                text = "The deposit amount should be between 500 and 1000 USDT!"
            await msg.answer(text)
    else:
        text = "Введите желаемую сумму пополнения числом, без запятых, букв и прочего!"
        if language[4] == "EN":
            text = "Please enter the desired deposit amount as a number, without commas, letters, or other symbols!"
        await msg.answer(text)


async def smalluser_amount_1000(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    if msg.text.isdigit():
        if int(msg.text) >= 1000:
            async with state.proxy() as data:
                summary = int(msg.text)
                response = await thedex.create_invoice(summary, msg.from_id, "Пополнение больше 1000")
                await state.update_data({'status': 1000, 'amount': int(msg.text), 'invoiceId': response})
                await thedex_db.insert_transaction(msg.from_id, int(msg.text), response)
                await users.set_status(status="1000", tg_id=msg.from_id)
                text = "Выберите длительность холда:"
                if language[4] == "EN":
                    text = "Select hold time:"
                await msg.answer(text, reply_markup=inline.hold_kb(language[4]))
                await state.set_state(SmallUser.hold.state)
        else:
            text = "Сумма пополнения должна быть от 1000 USDT!"
            if language[4] == "EN":
                text = "The deposit amount should be from 1000 USDT!"
            await msg.answer(text)
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
        text = "Выберите сеть пополнения:"
        if language[4] == "EN":
            text = "Select deposit cryptocurrency:"
        await call.message.answer(text, reply_markup=inline.return_currencies())
        await state.set_state(SmallUser.currency.state)


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
        text = f"Отправьте {count} {currency_str} на указанный адрес:\n\n`{wallet[0]}`\n\n" \
               f"Перед совершением транзакции внимательно проверьте адрес получателя и сумму перевода, оба значения " \
               f"должны совпадать со значениями в сообщении"

        if language[4] == "EN":
            text = f"Please send {count} {currency_str} to the provided address:\n\n{wallet[0]}\n\n" \
                   f"Before making the transaction, carefully verify the recipient's address and the transfer amount. " \
                   f"Both values should match the ones in the message."
        await call.message.answer(text, reply_markup=inline.finish_transaction(language[4]),
                                  parse_mode=types.ParseMode.MARKDOWN_V2)
    await SmallUser.next()


async def smalluser_finish(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    async with state.proxy() as data:
        status = await thedex.invoice_one(data.get('invoiceId'))
    if status == "Waiting":
        text = "Нужно еще немного времени на проверку, пожалуйста, повторите позже"
        if language[4] == "EN":
            text = "We need a little more time for verification. Please try again later"
        await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))
    if status == "Unpaid":
        text = "Вы не успели оплатить. Процедуру необходимо провести заново\n\n" \
               'Пожалуйста, напишите цифрами сумму депозита в USDT, которую хотели бы внести. \n\n' \
               'Минимальный вклад 500 USDT\n\n' \
               'Комиссия - 0,5%'
        if language[4] == "EN":
            text = "You missed the payment deadline. The procedure needs to be repeated.\n\n" \
                   "Please write the deposit amount in USDT as a number.\n\n" \
                   "Minimum deposit is 500 USDT.\n\n" \
                   "Commission fee - 0.5%."
        await state.set_state(SmallUser.amount.state)
        await call.message.answer(text)

    if status == "Successful":
        text = "Оплата прошла успешно."
        if language[4] == "EN":
            text = "Payment was successful."
        try:
            await balance.insert_deposit(call.from_user.id, data.get("amount"))
            await balance.insert_balance_history(call.from_user.id, data.get("amount"), data.get('invoiceId'))
            #await thedex_db.insert_status(call.from_user.id, row[2], status)
        except:
            pass
        await state.finish()
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))

    if status == "Rejected":
        text = "Произошла ошибка. Деньги вернуться к вам на счет."
        if language[4] == "EN":
            text = "An error occurred. The money will be refunded to your account."
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))


async def smalluser_check(call: types.CallbackQuery, row):
    language = await users.user_data(call.from_user.id)
    status = await thedex.invoice_one(row[2])
    if status == "Waiting":
        text = "Нужно еще немного времени на проверку, пожалуйста, повторите позже"
        if language[4] == "EN":
            text = "We need a little more time for verification. Please try again later."
        await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))

    if status == "Unpaid":
        text = "Вы не успели оплатить. Процедуру необходимо провести заново\n\n"
        if language[4] == "EN":
            text = "You missed the payment deadline. The procedure needs to be repeated.\n\n"
        await call.message.answer(text)
        await thedex_db.insert_status(call.from_user.id, row[2], status)
        call.data = "500"
        await registration_500(call)

    if status == "Successful":
        text = "Оплата прошла успешно."
        if language[4] == "EN":
            text = "Payment was successful."
        try:
            await balance.insert_deposit(call.from_user.id, row[1])
            await balance.insert_balance_history(call.from_user.id, row[1], row[2])
            await thedex_db.insert_status(call.from_user.id, row[2], status)
        except:
            pass
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))

    if status == "Rejected":
        text = "Произошла ошибка. Деньги вернуться к вам на счет."
        if language[4] == "EN":
            text = "An error occurred. The money will be refunded to your account."
        await thedex_db.insert_status(call.from_user.id, row[2], status)
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))


async def smalluser_check_2(call: types.CallbackQuery):
    await call.message.delete()
    rows = await thedex_db.get_transaction(call.from_user.id)
    row = rows[0]
    language = await users.user_data(call.from_user.id)
    status = await thedex.invoice_one(row[2])
    if status == "Waiting":
        text = "Нужно еще немного времени на проверку, пожалуйста, повторите позже"
        if language[4] == "EN":
            text = "We need a little more time for verification. Please try again later."
        await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))

    if status == "Unpaid":
        text = "Вы не успели оплатить. Процедуру необходимо провести заново\n\n"
        if language[4] == "EN":
            text = "You missed the payment deadline. The procedure needs to be repeated.\n\n"
        await call.message.answer(text)
        await thedex_db.insert_status(call.from_user.id, row[2], status)
        call.data = "500"
        await registration_500(call)

    if status == "Successful":
        text = "Оплата прошла успешно."
        if language[4] == "EN":
            text = "Payment was successful."
        try:
            await balance.insert_deposit(call.from_user.id, row[1])
            await balance.insert_balance_history(call.from_user.id, row[1], row[2])
            await thedex_db.insert_status(call.from_user.id, row[2], status)
        except:
            pass
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))

    if status == "Rejected":
        text = "Произошла ошибка. Деньги вернуться к вам на счет."
        if language[4] == "EN":
            text = "An error occurred. The money will be refunded to your account."
        await thedex_db.insert_status(call.from_user.id, row[2], status)
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))


async def transiction_detail(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    rows = await thedex_db.get_transaction(call.from_user.id)
    row = rows[0]
    status = await thedex.invoice_one_2(row[2])
    count = status[3]
    try:
        if "." in count:
            count = count.replace(".", ",")
        text = f"<b>Сумма к оплате:</b><em> {count} {status[2]} </em>\n" \
               f"<b>Статус оплаты:</b><em> {status[0]}</em>\n" \
               f"<b>Кошелек для оплаты:</b><em> {status[1]}</em>\n"

        if language[4] == "EN":
            text = f"<b>Payment amount:</b><em> {count} {status[2]} </em>\n" \
                   f"<b>Payment status:</b><em> {status[0]}</em>\n" \
                   f"<b>Payment wallet:</b><em> {status[1]}</em>\n"
        await call.message.answer(text, reply_markup=inline.transaction_status(language[4]))
    except TypeError:
        text = "Ошибка транзакции, попробуйте повторить еще раз!"
        if language[4] == "EN":
            text = f"Transaction error, please repeat one more time!"
        await call.message.answer(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
        await thedex_db.delete_transaction(row[0])


def register(dp: Dispatcher):
    dp.register_callback_query_handler(registration_500, text='500')
    dp.register_callback_query_handler(deposit_500, lambda c: c.data in ['from_500', 'from_1000'])
    dp.register_message_handler(smalluser_amount_1000, state=SmallUser.amount_1000)
    dp.register_message_handler(smalluser_step1, state=SmallUser.amount)
    dp.register_callback_query_handler(smalluser_hold, state=SmallUser.hold)
    dp.register_callback_query_handler(smalluser_step2, state=SmallUser.currency)
    dp.register_callback_query_handler(smalluser_finish, state=SmallUser.finish)
    dp.register_callback_query_handler(smalluser_check_2, text="transaction_status")
    dp.register_callback_query_handler(transiction_detail, text="transaction_detail", state="*")
