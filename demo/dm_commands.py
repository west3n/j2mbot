import asyncio

import decouple
import psycopg2
from aiogram import Dispatcher, types
from aiogram.utils.exceptions import MessageToDeleteNotFound

from demo import dm_inline, dm_database
from database import nft, users


async def j2mdemo_handler(msg: types.Message):
    await msg.delete()
    nft_status = nft.check_nft_status(msg.from_id)
    language = await users.user_data(msg.from_user.id)
    name = msg.from_user.first_name
    if nft_status:
        try:
            await dm_database.insert_demo_mode(msg.from_id)
        except psycopg2.Error:
            pass
        text_1 = 'В демо-режиме для вас доступен Баланс, Пополнение и Вывод. ' \
                 'При нажатии на остальные кнопки демо-режим закончится. ' \
                 '\n\nЭто сообщение будет автоматически удалено через 10 секунд.'
        text = f"{name}, выберите интересующий Вас раздел, нажав одну из кнопок ниже"
        photo = decouple.config("BANNER_MAIN")
        if language[4] == 'EN':
            text_1 = 'In demo mode, you have access to balance, deposit, and withdrawal. ' \
                     'Pressing other buttons will end the demo mode.' \
                     '\n\nThis message will be automatically deleted in 10 seconds.'
            text = f"{name}, please select the section of interest by clicking one of the buttons below:"
            photo = decouple.config("BANNER_MAIN_EN")
        message = await msg.answer(text_1)
        await asyncio.sleep(10)
        await msg.bot.delete_message(msg.chat.id, message.message_id)
        await msg.answer_photo(photo, text, reply_markup=await dm_inline.dm_main_menu(language[4]))
    else:
        text = 'Демо-режим для вас недоступен'
        if language[4] == 'EN':
            text = 'Demo mode is not available for you.'
        await msg.answer(text)


async def dm_bot_start_call(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = "Загружаю главное меню..."
    if language[4] == 'EN':
        text = "Loading main menu..."
    start_message = await call.message.answer(text)
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    name = call.from_user.first_name
    language = await users.user_data(call.from_user.id)
    text = f"{name}, выберите интересующий Вас раздел, нажав одну из кнопок ниже"
    photo = decouple.config("BANNER_MAIN")
    if language[4] == 'EN':
        text = f"{name}, please select the section of interest by clicking one of the buttons below:"
        photo = decouple.config("BANNER_MAIN_EN")
    try:
        await call.message.bot.delete_message(call.message.chat.id, start_message.message_id)
    except MessageToDeleteNotFound:
        pass
    await call.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=await dm_inline.dm_main_menu(language[4]))


def register(dp: Dispatcher):
    dp.register_message_handler(j2mdemo_handler, commands='j2mdemo')
    dp.register_callback_query_handler(dm_bot_start_call, text='dm_main_menu')
