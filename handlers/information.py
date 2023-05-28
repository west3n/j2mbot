import decouple
from aiogram import Dispatcher, types
from keyboards import inline
from database import users


async def information_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_INFORMATION")
    text = "Здесь вы можете изучить FAQ"
    if language[4] == 'EN':
        photo = decouple.config("BANNER_INFORMATION_EN")
        text = "FAQ"
    await call.message.delete()
    await call.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=inline.information_menu(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(information_handler, text='information')
