import decouple
import handlers.commands

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import inline
from database import users, balance, output


class NewWallet(StatesGroup):
    wallet = State()
    amount = State()


async def withdrawal_handler(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_WITHDRAWAL")
    balance_history = await balance.get_withdrawal_history(call.from_user.id)
    withdrawal_balance = 0
    wallet = await users.user_data(call.from_user.id)
    if not wallet[6] and balance_history[0] == 0:
        text = "Для того, чтобы вывести средства, нужно добавить адрес кошелька для вывода.\n\n " \
               "Вы всегда сможете изменить его в меню 'Баланс' в разделе 'Информация'."
        if language[4] == 'EN':
            photo = decouple.config("BANNER_WITHDRAWAL_EN")
            text = "To withdraw funds, you need to add a withdrawal wallet address.\n\n"
            "You can always change it in the 'Balance' menu in the 'Information' section."
        await call.message.delete()
        await call.message.answer_photo(photo=photo, caption=text)
        await NewWallet.wallet.set()
    else:
        await state.set_state(NewWallet.amount.state)
        text = f"Баланс, доступный к выводу: {withdrawal_balance} USDT" \
               f"\nCумма минимального вывода 50 USDT" \
               f"\n\nНапишите сумму USDT, которую хотите вывести:"
        if language[4] == 'EN':
            text = f"The balance available for withdrawal: {withdrawal_balance} USDT" \
                   f"\nMinimum withdrawal amount is 50 USDT." \
                   f"\n\nPlease write the amount of USDT you want to withdraw:"
        await call.message.delete()
        await call.message.answer(text)


async def add_new_wallet(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['wallet'] = msg.text
    await users.save_wallet(data.get('wallet'), msg.from_id)
    text = 'Ваш номер кошелька добавлен. Вы хотите блаблабла?'
    if language[4] == 'EN':
        text = "Your wallet number has been added. Do you want to blah blah blah?"
    await msg.answer(text, reply_markup=inline.withdrawal_confirmation(language[4]))


async def insert_amount(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'withdrawal_confirmation':
        await state.set_state(NewWallet.amount.state)
        text = "Напишите сумму USDT, которую хотите вывести:"
        if language[4] == 'EN':
            text = "Please indicate the amount of USDT you wish to withdraw:"
        await call.message.edit_text(text)
    else:
        await handlers.commands.bot_start_call(call)
        await state.finish()


async def handle_amount(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    if not msg.text.isdigit():
        text = 'Пожалуйста, используйте только цифры!'
        if language[4] == 'EN':
            text = 'Please, use digits only!'
        await msg.delete()
        await msg.answer(text)
    else:
        async with state.proxy() as data:
            data['amount'] = msg.text
        wallet = await users.user_data(msg.from_user.id)
        text = f"Вы заказываете вывод {data.get('amount')} USDT на TRC-20 кошелёк {wallet[6]}\n\n" \
               f" блаблабла"
        if language[4] == "EN":
            text = f"You are requesting a withdrawal of {data.get('amount')} USDT to TRC-20 wallet {wallet[6]}.\n\n" \
                   f"Blah blah blah."
        await msg.answer(text, reply_markup=inline.finish_withdrawal(language[4]))


async def finish_withdrawal(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'confirm_withdrawal':
        await call.message.delete()
        await call.bot.send_chat_action(call.message.chat.id, 'typing')
        wallet = await users.user_data(call.from_user.id)
        async with state.proxy() as data:
            await output.insert_new_output(call.from_user.id, data.get('amount'), wallet[6])
            await balance.save_withdrawal_amount(data.get('amount'), call.from_user.id)
            text = f'Создан запрос на вывод {data.get("amount")} USDT TRC-20 (кошелёк {wallet[6]}' \
                   f'\n\nМы выгружаем блаблабла'
            if language[4] == 'EN':
                text = f"A withdrawal request for {data.get('amount')} USDT TRC-20 (wallet {wallet[6]}) " \
                       f"has been created.\n\nWe are processing the blah blah blah."
        await call.message.answer(text, reply_markup=inline.back_button(language[4]))
        await state.finish()
    else:
        text = 'Вы отменили операцию!'
        if language[4] == "EN":
            text = 'Operation canceled!'
        await call.message.edit_text(text)
        await handlers.commands.bot_start_call(call)
        await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(withdrawal_handler, text='withdrawal')
    dp.register_message_handler(add_new_wallet, state=NewWallet.wallet)
    dp.register_callback_query_handler(insert_amount, state=NewWallet.wallet)
    dp.register_message_handler(handle_amount, state=NewWallet.amount)
    dp.register_callback_query_handler(finish_withdrawal, state=NewWallet.amount)
