import decouple
from aiogram import Dispatcher, types
from keyboards import inline
from database import users, balance, referral
from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    language = State()
    accept = State()
    finish = State()


async def bot_start(msg: types.Message):
    user_status = await users.user_data(msg.from_user.id)
    wallet = await balance.get_balance_status(msg.from_id)
    if user_status and wallet:
        name = msg.from_user.first_name
        language = await users.user_data(msg.from_user.id)
        text = f"Привет, {name}! Здесь будет текст приветствия!"
        photo = decouple.config("BANNER_MAIN")
        if language[4] == 'EN':
            text = f'Hello, {name}! There will be greetings text!'
            photo = decouple.config("BANNER_MAIN_EN")
        await msg.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=inline.main_menu(language[4]))
    elif user_status:
        name = msg.from_user.first_name
        language = await users.user_data(msg.from_user.id)
        text = f"Привет, {name}! Здесь будет текст приветствия!"
        photo = decouple.config("BANNER_MAIN")
        if language[4] == 'EN':
            text = f'Hello, {name}! There will be greetings text!'
            photo = decouple.config("BANNER_MAIN_EN")
        await msg.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=inline.main_menu_short(language[4]))
    else:
        await msg.answer("Выберете язык бота: / Select bot language:",
                         reply_markup=inline.language())
        await Registration.language.set()
    if msg.get_args():
        if int(msg.get_args()) == msg.from_id:
            pass
        else:
            await referral.add_first_line(int(msg.get_args()), msg.from_id)


async def bot_start_call(call: types.CallbackQuery):
    photo = decouple.config("BANNER_MAIN")
    name = call.from_user.first_name
    language = await users.user_data(call.from_user.id)
    wallet = await balance.get_balance_status(call.from_user.id)
    text = f"Привет, {name}! Здесь будет текст приветствия!"
    if language[4] == 'EN':
        text = f'Hello, {name}! There will be greetings text!'
        photo = decouple.config("BANNER_MAIN_EN")
    if wallet:
        await call.message.delete()
        await call.message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=inline.main_menu(language[4]))
    else:
        await call.message.delete()
        await call.message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=inline.main_menu_short(language[4]))


async def select_language(msg: types.Message):
    await msg.answer("Выберете язык бота:\nSelect bot language:",
                     reply_markup=inline.language())
    await Registration.language.set()


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
    dp.register_message_handler(select_language, commands='language', state='*')
    dp.register_callback_query_handler(bot_start_call, text='main_menu')
