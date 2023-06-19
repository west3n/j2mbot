from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from database import users, balance, thedex_db
from keyboards import inline


class SmallUser(StatesGroup):
    amount_1000 = State()
    amount = State()


async def registration_500(call: types. CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'Здесь будет текст с условием размещения криптоактивов'
    if language[4] == 'EN':
        text = 'Text describing the terms and conditions for cryptocurrency placement will be placed here.'
    await call.message.edit_text(text, reply_markup=inline.refill_500_choice(language[4]))


async def deposit_500(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'from_500':
        text = 'Пожалуйста, напишите цифрами сумму депозита в USDT, которую хотели бы внести. \n\n' \
               'Минимальный вклад 500 USDT'
        if language[4] == 'EN':
            text = "Enter the replenishment amount in USDT using digits.\n"
            "Minimum amount - 500 USDT\n"
            "Maximum amount - 999 USDT\n"
            "When replenishing, you also pay for the cost of AML verification, which is 0.5% of the replenishment amount."
        await call.message.edit_text(text)
        await SmallUser.amount.set()
    elif call.data == 'from_1000':
        text = 'Пожалуйста, напишите цифрами сумму депозита в USDT, которую хотели бы внести. \n\n' \
               'Минимальный вклад 1000 USDT'
        if language[4] == 'EN':
            text = "Enter the replenishment amount in USDT using digits.\n"
            "Minimum amount - 1000 USDT\n"
            "When replenishing, you also pay for the cost of AML verification, which is 0.5% of the replenishment amount."
        await call.message.edit_text(text)
        await SmallUser.amount.set()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(registration_500, text='500')
    dp.register_callback_query_handler(deposit_500, lambda c: c.data in ['from_500', 'from 1000'])
