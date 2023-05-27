import decouple
from aiogram import Dispatcher, types
from keyboards import inline
from database import users


async def withdrawal_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_WITHDRAWAL")
    text = "Раздел 'Вывод' находится в процессе разработки"
    if language[4] == 'EN':
        photo = decouple.config("BANNER_WITHDRAWAL_EN")
        text = "The 'Withdrawal' section is currently under development"
    await call.message.delete()
    await call.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=inline.back_button(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(withdrawal_handler, text='withdrawal')
