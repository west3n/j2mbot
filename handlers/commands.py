from aiogram import Dispatcher, types


async def bot_start(msg: types.Message):
    photo_path = 'media/banner.jpg'
    name = msg.from_user.first_name
    with open(photo_path, 'rb') as photo:
        await msg.answer_photo(
            photo=photo,
            caption=f"Привет, {name}! Здесь будет текст приветствия!")


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
