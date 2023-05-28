import decouple
import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from database import users
from handlers import commands
from keyboards import inline
from handlers.commands import Registration


async def language_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['language'] = call.data.upper()
    user_status = await users.user_data(call.from_user.id)
    if user_status:
        if call.data in ['ru', 'en']:
            await users.update_user_language(call.from_user.id, call.data.upper())
            await commands.bot_start_call(call)
            await state.finish()
    else:
        text_1 = "Пожалуйста, ознакомьтесь с пользовательским соглашением и примите условия."
        text_2 = "Принимаете условия пользовательского соглашения?"
        document = decouple.config("USER_AGREEMENT")
        if call.data == 'en':
            text_1 = "Please read the user agreement and accept the terms."
            text_2 = "Do you accept the terms of the user agreement?"
            document = decouple.config("USER_AGREEMENT_EN")
        message = await call.message.edit_text(text_1)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(2)
        await call.message.answer_document(document)
        await call.message.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(3)
        await call.bot.delete_message(chat_id=call.message.chat.id,
                                      message_id=message.message_id)
        await call.message.answer(text_2, reply_markup=inline.user_terms(call.data.upper()))
        await Registration.next()


async def handle_user_terms_kb(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await call.message.edit_reply_markup(reply_markup=inline.user_terms_2(data.get("language")))
    await Registration.next()


async def finish_registration(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == "terms_accept":
            await call.message.edit_reply_markup(reply_markup=inline.user_terms(data.get('language')))
            await state.set_state(Registration.accept.state)
        else:
            await users.add_new_user(call.from_user.id, call.from_user.username,
                                     call.from_user.full_name, data.get('language'))
            await state.finish()
            await commands.bot_start_call(call)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(language_handler, state=Registration.language)
    dp.register_callback_query_handler(handle_user_terms_kb, state=Registration.accept)
    dp.register_callback_query_handler(finish_registration, state=Registration.finish)
