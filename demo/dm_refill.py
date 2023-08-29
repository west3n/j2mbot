import asyncio
import random
import decouple
import shutup

from aiogram.utils.exceptions import BadRequest, MessageToDeleteNotFound
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from demo import dm_inline, dm_database
from database import users, documents


shutup.please()


class DemoNewDoc(StatesGroup):
    docs = State()
    docs_2 = State()


class DemoBigUser(StatesGroup):
    binance = State()
    kyc = State()
    contract = State()
    finish = State()


class DemoBinanceAPI(StatesGroup):
    alias = State()


class DemoRefill(StatesGroup):
    count = State()


async def refill_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_REFILL")
    text = await users.get_text('Главное меню пополнения (1000)', language[4])
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    await call.message.answer_photo(photo, text, reply_markup=dm_inline.dm_refill_main_menu(language[4]))


async def handle_deposit_funds(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'Выберите один из вариантов:'
    if language[4] == "EN":
        text = 'Select at least one option:'
    await call.message.delete()
    await call.message.answer(text, reply_markup=dm_inline.dm_refill_account_2(language[4]))


async def handle_review_terms(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Дисклеймер (пополнение)', language[4])
    await call.message.delete()
    await call.message.answer(text, reply_markup=dm_inline.dm_distribution(language[4]))


async def handle_distribution(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Описание категорий (пополнение)', language[4])
    await call.message.edit_text(text, reply_markup=dm_inline.dm_refill_account_3(language[4]))


async def handle_500_15000(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'dm_active_50':
        text = await users.get_text('Описание категории 1 (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=dm_inline.dm_active_50(language[4]))
    elif call.data == 'dm_active_5000':
        text = await users.get_text('Описание категории 2 (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=dm_inline.dm_active_5000(language[4]))
    else:
        text = await users.get_text('Описание категории 3 (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=dm_inline.dm_active_15000(language[4]))


async def stabpool_terms(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Описание стабпула (пополнение)', language[4])
    await call.message.edit_text(text, reply_markup=dm_inline.stabpool_kb_dm(language[4]))


async def handle_partners(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Условия партнерской программы (пополнение)', language[4])
    text = text.replace('{этой таблице}', "<a href='https://drive.google.com/file/d/1ZhHtNpsE"
                                          "5Y8l1i5n6Mp1UtG44uOMiKnP/view?pli=1'>этой таблице.</a>")
    if language[4] == 'EN':
        text = text.replace('этой таблице', 'this table')
    await call.message.edit_text(text, reply_markup=dm_inline.dm_partners_kb(language[4]))


async def biguser_registration(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    status = await dm_database.get_demo_balance(call.from_user.id)
    if status[3] == "ДЕМО":
        await main_refill_menu(call)
    else:
        text = await users.get_text('Регистрация личного аккаунта #1', language[4])
        text_2 = await users.get_text('Регистрация личного аккаунта #2', language[4])
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        mess = await call.message.answer(text)
        await call.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(3)
        await call.bot.delete_message(call.from_user.id, mess.message_id)
        await call.message.answer(text_2, reply_markup=dm_inline.dm_yesno(language[4]))
        await DemoBigUser.binance.set()


async def new_docs(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    document = decouple.config('BALANCE_DOCUMENT')
    text = await users.get_text('Отправка приложения №1 (пополнение)', language[4])
    await call.bot.send_chat_action(chat_id=call.from_user.id, action="upload_document")
    await asyncio.sleep(2)
    await call.bot.send_document(chat_id=call.from_user.id, document=document)
    await call.message.answer(text, reply_markup=dm_inline.dm_user_terms(language[4]))
    await DemoNewDoc.docs.set()


async def new_docs_2(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=dm_inline.dm_user_terms_2(language[4]))
    await DemoNewDoc.next()


async def new_docs_3(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == "dm_terms_accept":
        await call.message.edit_reply_markup(reply_markup=dm_inline.dm_user_terms(language[4]))
        await state.set_state(DemoNewDoc.docs.state)
    else:
        await state.finish()
        await call.message.delete()
        await biguser_registration(call)


async def biguser_registration_step_1(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'dm_no':
        text = await users.get_text('KYC (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=await dm_inline.dm_main_menu(language[4]))
        await state.finish()
    else:
        text = await users.get_text('KYC (пополнение) #2', language[4])
        await call.message.edit_text(text, reply_markup=dm_inline.dm_yesno(language[4]))
        await DemoBigUser.next()


async def biguser_registration_step_2(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'dm_no':
        text = await users.get_text('KYC (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=await dm_inline.dm_main_menu(language[4]))
        await state.finish()
    else:
        text = await users.get_text('Отправка договора (пополнение)', language[4])
        contract = decouple.config("CONTRACT")
        if language[4] == "EN":
            contract = decouple.config("CONTRACT_EN")
        await call.message.delete()
        await call.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(2)
        await call.message.answer_document(contract)
        await documents.update_kyc(call.from_user.id)
        await call.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(2)
        await call.message.answer(text, reply_markup=dm_inline.dm_emailing_documents(language[4]))
        await state.finish()


async def handle_emailing_documents(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Оповещение администратору (пополнение)', language[4])
    try:
        await call.message.edit_text(text)
    except BadRequest:
        await call.message.delete()
        await call.message.answer(text)
    await state.finish()
    await asyncio.sleep(10)
    text = await users.get_text('Alias (пополнение)', language[4])
    text = text.replace('{ссылкa}', "<a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera"
                                    "-saina-instrukciya'>ссылке</a>")
    if language[4] == "EN":
        text = text.replace('ссылке', 'link')
    await call.message.answer(text)
    await asyncio.sleep(5)
    await binanceapi_step1_call(call)


async def binanceapi_step1_call(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    text = await users.get_text('Alias (пополнение)', language[4])
    text = text.replace('{ссылкa}', "<a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera"
                                    "-saina-instrukciya'>ссылке</a>")
    if language[4] == "EN":
        text = text.replace('ссылке', 'link')
    await call.message.answer(text, reply_markup=dm_inline.dm_emailing_alias(language[4]))
    await DemoBinanceAPI.alias.set()


async def handle_emailing_alias(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Оповещение администратору (пополнение)', language[4])
    await call.message.edit_text(text)
    await state.finish()
    await asyncio.sleep(10)
    text = f"<b>Администратор подтвердил ваши данные по API KEY, API SECRET, Alias</b>"
    if language == "EN":
        text = f"<b>The administrator has confirmed your API KEY, API SECRET, and Alias.</b>"
    await call.message.answer(text)
    await asyncio.sleep(3)
    await main_refill_menu(call)


async def main_refill_menu(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    text = f"<b>Введите сумму для пополнения:</b>"
    if language[4] == "EN":
        text = "Please enter the amount to deposit:"
    await call.message.answer(text)
    await DemoRefill.count.set()


async def count_refill(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    x = [25380, 25621, 25342, 26100, 25432, 25407, 25002, 25977, 25211]
    balance_binance = random.choice(x)
    if msg.text.isdigit():
        if int(msg.text) >= 15000:
            async with state.proxy() as data:
                data['count'] = msg.text
            if balance_binance >= 15000 and balance_binance > int(msg.text):
                deposit = await dm_database.get_demo_balance(msg.from_id)
                await dm_database.update_demo_personal_balance(msg.from_id, int(msg.text), balance_binance)
                await dm_database.insert_demo_balance_history(msg.from_id, int(msg.text), "IN", "Личный аккаунт")
                text = await users.get_text('Успешное пополнение', language[4])
                text = text.replace('{баланс}', f'{balance_binance}').replace("{депозит}", f"{deposit[7]}")
                await msg.answer(text, reply_markup=await dm_inline.dm_main_menu(language[4]))
                await state.finish()
            else:
                text = await users.get_text('Ошибка пополнения #1', language[4])
                text = text.replace("{сумма}", f'{int(msg.text) - int(balance_binance)}')
                await msg.answer(text)
                await state.finish()
        else:
            deposit = await dm_database.get_demo_balance(msg.from_id)
            if int(deposit[7]) + int(msg.text) >= 25000:
                if int(balance_binance) >= int(msg.text):
                    await dm_database.update_demo_personal_balance(msg.from_id, int(msg.text), balance_binance)
                    await dm_database.insert_demo_balance_history(msg.from_id, int(msg.text), "IN", "Личный аккаунт")
                    text = await users.get_text('Успешное пополнение', language[4])
                    text = text.replace('{баланс}', f'{balance_binance}').replace("{депозит}", f"{int(deposit[7])}")
                    await msg.answer(text, reply_markup=await dm_inline.dm_main_menu(language[4]))
                    await state.finish()
                else:
                    x = int(msg.text)
                    if 25000 > int(msg.text):
                        x = 25000
                    text = await users.get_text('Ошибка пополнения #1', language[4])
                    text = text.replace("{сумма}", f'{x - int(balance_binance)}')
                    await msg.answer(text)
                    await state.finish()
            else:
                text = await users.get_text('Ошибка пополнения #2', language[4])
                await msg.answer(text)
    else:
        text = await users.get_text('Ошибка пополнения #3', language[4])
        await msg.answer(text)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(refill_handler, text='dm_refill', state="*")
    dp.register_callback_query_handler(handle_deposit_funds, text='dm_deposit_funds')
    dp.register_callback_query_handler(handle_review_terms, text='dm_review_terms')
    dp.register_callback_query_handler(handle_distribution, text='dm_distribution')
    dp.register_callback_query_handler(stabpool_terms, text='dm_stabpool_terms')
    dp.register_callback_query_handler(handle_partners, text='dm_partners')
    dp.register_callback_query_handler(handle_500_15000,
                                       lambda c: c.data in ['dm_active_50', 'dm_active_5000', 'dm_active_15000'])
    dp.register_callback_query_handler(handle_emailing_documents, text='dm_emailing_documents')
    dp.register_callback_query_handler(handle_emailing_alias, state=DemoBinanceAPI.alias)
    dp.register_callback_query_handler(biguser_registration, text="dm_15000")
    dp.register_callback_query_handler(biguser_registration_step_1, state=DemoBigUser.binance)
    dp.register_callback_query_handler(biguser_registration_step_2, state=DemoBigUser.kyc)
    dp.register_message_handler(count_refill, state=DemoRefill.count)
    dp.register_callback_query_handler(new_docs_2, state=DemoNewDoc.docs)
    dp.register_callback_query_handler(new_docs_3, state=DemoNewDoc.docs_2)
