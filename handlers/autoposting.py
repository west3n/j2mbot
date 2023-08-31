from aiogram import Dispatcher, types
from database import autoposting_db


async def handle_autoposting(call: types.CallbackQuery):
    confirm = call.data.split('_')[1]
    post_id = call.data.split('_')[2]
    if confirm == 'yes':
        await autoposting_db.approve_post(post_id)
        await call.message.answer(f"Задача отправлена в автопостинг!")
        await call.message.delete_reply_markup()
    else:
        await call.message.answer(f"Задача отправлена на доработку!")
        await call.message.delete_reply_markup()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(handle_autoposting, lambda c: c.data.startswith('autoposting'))
