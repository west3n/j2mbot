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
           "<em>По умолчанию реинвестируется 100%<em>"
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
    language = await users.user_data(call.from_user.id)
    balance_history = await balance.get_withdrawal_history(call.from_user.id)
    withdrawal_balance = await balance.get_my_balance(call.from_user.id)
    wallet = await users.user_data(call.from_user.id)
    print(wallet[6])
    if not wallet[6]:
        text = "Для того, чтобы вывести средства, нужно добавить адрес кошелька для вывода.\n" \
               "Ответным сообщением пришлите адрес кошелька <b>TRC-20 USDT</b>\n\n" \
               "Вы всегда сможете изменить его в меню 'Вывод'."
        if language[4] == 'EN':
            text = "To withdraw funds, you need to add a withdrawal wallet address.\n\n"
            "You can always change it in the 'Withdrawal' section."
        await call.message.delete()
        await call.message.answer(text)
        await NewWallet.wallet.set()
    if withdrawal_balance is None or 0:
        await state.set_state(NewWallet.amount.state)
        text = f"<b>Баланс, доступный к выводу:</b> {withdrawal_balance if withdrawal_balance is not None else 0} USDT"
        if language[4] == 'EN':
            text = f"<b>The balance available for withdrawal:</b> {withdrawal_balance if withdrawal_balance is not None else 0} USDT"
        await call.message.delete()
        await state.finish()
        await call.message.answer(text, reply_markup=inline.main_menu(language[4]))

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
    dp.register_callback_query_handler(withdraw_main_menu, text='withdrawal')
    dp.register_callback_query_handler(withdrawal_handler, text='withdrawal_funds')
    dp.register_callback_query_handler(change_wallet_new, text='change_wallet')
    dp.register_message_handler(change_wallet_step2, state=ChangeWallet.wallet)
    dp.register_message_handler(add_new_wallet, state=NewWallet.wallet)
    dp.register_callback_query_handler(insert_amount, state=NewWallet.wallet)
    dp.register_message_handler(handle_amount, state=NewWallet.amount)
    dp.register_callback_query_handler(finish_withdrawal, state=NewWallet.amount)
