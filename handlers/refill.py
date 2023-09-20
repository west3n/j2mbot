import asyncio
import random
import decouple
import shutup

from aiogram.utils.exceptions import BadRequest, MessageToDeleteNotFound
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import inline
from database import users, documents, binance_db, balance, thedex_db
from binance import actions as binance
from handlers.refill_500 import registration_500
from ccxt.base.errors import AuthenticationError

shutup.please()


class NewDoc(StatesGroup):
    docs = State()
    docs_2 = State()


class DocsAccept(StatesGroup):
    accept = State()
    finish = State()
    referral = State()
    new_referral = State()


class BigUser(StatesGroup):
    binance = State()
    kyc = State()
    contract = State()
    finish = State()


class BinanceAPI(StatesGroup):
    alias = State()


class Refill(StatesGroup):
    count = State()


async def refill_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    trans = await thedex_db.get_transaction(call.from_user.id)
    photo = decouple.config("BANNER_REFILL")
    if not trans:
        text = await users.get_text('Главное меню пополнения (1000)', language[4])
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        await call.message.answer_photo(photo, text, reply_markup=inline.refill_main_menu(language[4]))
    else:
        await registration_500(call)


async def handle_deposit_funds(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'Выберите один из вариантов:'
    if language[4] == "EN":
        text = 'Select at least one option:'
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    await call.message.answer(text, reply_markup=inline.refill_account_2(language[4]))


async def handle_review_terms(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Дисклеймер (пополнение)', language[4])
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.distribution(language[4]))


async def handle_distribution(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Описание категорий (пополнение)', language[4])
    await call.message.edit_text(text, reply_markup=inline.refill_account_3(language[4]))


async def handle_500_15000(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'active_50':
        text = await users.get_text('Описание категории 1 (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=inline.active_50(language[4]))
    elif call.data == 'active_5000':
        text = await users.get_text('Описание категории 2 (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=inline.active_5000(language[4]))
    else:
        text = await users.get_text('Описание категории 3 (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=inline.active_15000(language[4]))


async def stabpool_terms(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Описание стабпула (пополнение)', language[4])
    await call.message.edit_text(text, reply_markup=inline.stabpool_kb(language[4]))


async def handle_partners(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Условия партнерской программы (пополнение)', language[4])
    text = text.replace('{этой таблице}', "<a href='https://drive.google.com/file/d/1ZhHtNpsE"
                                          "5Y8l1i5n6Mp1UtG44uOMiKnP/view?pli=1'>этой таблице.</a>")
    if language[4] == 'EN':
        text = text.replace('этой таблице', 'this table')
    await call.message.edit_text(text, reply_markup=inline.partners_kb(language[4]))


async def biguser_registration(call: types.CallbackQuery):
    first_check = await documents.check_it_product(call.from_user.id)
    second_check = await documents.check_kyc(call.from_user.id)
    language = await users.user_data(call.from_user.id)
    if first_check:
        if not second_check[0]:
            text = await users.get_text('Регистрация личного аккаунта #1', language[4])
            text_2 = await users.get_text('Регистрация личного аккаунта #2', language[4])
            try:
                await call.message.delete()
            except MessageToDeleteNotFound:
                pass
            mess = await call.message.answer(text)
            await call.bot.send_chat_action(call.message.chat.id, "typing")
            await asyncio.sleep(5)
            await call.bot.delete_message(call.from_user.id, mess.message_id)
            await call.message.answer(text_2, reply_markup=inline.yesno(language[4]))
            await BigUser.binance.set()
        else:
            contract = await documents.check_approve_contract(call.from_user.id)
            if contract[0] is False:
                text = await users.get_text('Ожидание подтверждения документов (пополнение) (1000)', language[4])
                await call.message.delete()
                await call.message.answer_document(document=decouple.config("CONTRACT"), caption=text,
                                                   reply_markup=inline.emailing_documents(language[4]))
            else:
                await binanceapi_step1_call(call)
    else:
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        await new_docs(call)


async def new_docs(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    document = decouple.config('BALANCE_DOCUMENT')
    text = await users.get_text('Отправка приложения №1 (пополнение)', language[4])
    await call.bot.send_chat_action(chat_id=call.from_user.id, action="upload_document")
    await asyncio.sleep(2)
    await call.bot.send_document(chat_id=call.from_user.id, document=document)
    await call.message.answer(text, reply_markup=inline.user_terms(language[4]))
    await NewDoc.docs.set()


async def new_docs_2(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=inline.user_terms_2(language[4]))
    await NewDoc.next()


async def new_docs_3(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == "terms_accept":
        await call.message.edit_reply_markup(reply_markup=inline.user_terms(language[4]))
        await state.set_state(NewDoc.docs.state)
    else:
        await state.finish()
        await call.message.delete()
        await documents.insert_it_product(call.from_user.id)
        await biguser_registration(call)


async def biguser_registration_step_1(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'no':
        text = await users.get_text('KYC (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
        await state.finish()
    else:
        text = await users.get_text('KYC (пополнение) #2', language[4])
        await call.message.edit_text(text, reply_markup=inline.yesno(language[4]))
        await BigUser.next()


async def biguser_registration_step_2(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'no':
        text = await users.get_text('KYC (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
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
        await call.message.answer(text, reply_markup=inline.emailing_documents(language[4]))
        await state.finish()


async def handle_emailing_documents(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Оповещение администратору (пополнение)', language[4])
    try:
        await call.message.edit_text(text)
    except BadRequest:
        await call.message.delete()
        await call.message.answer(text)
    await call.bot.send_message(chat_id=decouple.config('GROUP_ID'),
                                text=f"Пользователь {call.from_user.id} - {call.from_user.username} отправил контракт "
                                     f"для проверки:"
                                     f"\n\nПодробнее по ссылке: http://89.223.121.160:8000/admin/app/documents/")
    await state.finish()


async def binanceapi_step1_msg(message: types.Message):
    x = await documents.check_approve_contract(message.from_id)
    if x is True:
        binance_keys = await binance_db.check_binance_keys(message.from_id)
        if not binance_keys:
            language = await users.user_data(message.from_user.id)
            text = await users.get_text('Alias (пополнение)', language[4])
            text = text.replace('{ссылкa}', "<a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera"
                                            "-saina-instrukciya'>ссылке</a>")
            if language[4] == "EN":
                text = text.replace('ссылке', 'link')
            await message.answer(text, reply_markup=inline.emailing_alias(language[4]))
            await BinanceAPI.alias.set()
        else:
            pass
    else:
        pass


async def binanceapi_step1_call(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    y = await documents.check_approve_contract(call.from_user.id)
    if y[0] is True:
        x = await binance_db.check_binance_keys(call.from_user.id)
        try:
            x = x[0]
        except TypeError:
            x = None
        if not x:
            await call.message.delete()
            text = await users.get_text('Alias (пополнение)', language[4])
            text = text.replace('{ссылкa}', "<a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera"
                                            "-saina-instrukciya'>ссылке</a>")
            if language[4] == "EN":
                text = text.replace('ссылке', 'link')
            await call.message.answer(text, reply_markup=inline.emailing_alias(language[4]))
            await BinanceAPI.alias.set()
        else:
            await main_refill_menu(call)
    else:
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        text = await users.get_text('Оповещение администратору (пополнение) #2', language[4])
        await call.message.answer(text)


async def handle_emailing_alias(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Оповещение администратору (пополнение)', language[4])
    await call.message.edit_text(text)
    await call.bot.send_message(chat_id=decouple.config('GROUP_ID'),
                                text=f"Пользователь {call.from_user.id} - {call.from_user.username} "
                                     f"отправил API_KEY, API_SECRET, Alias на почту для проверки!"
                                     f"\n\nСоздайте запись в админ-панели: "
                                     f"http://89.223.121.160:8000/admin/app/binance/")
    await state.finish()


async def main_refill_menu(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    text = f"<b>Введите сумму для пополнения:</b>"
    if language[4] == "EN":
        text = "Please enter the amount to deposit:"
    await call.message.answer(text)
    await Refill.count.set()


async def count_refill(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    ad = await binance_db.check_binance_keys(msg.from_id)
    if ad[1] == "Реклама":
        x = [25380, 25621, 25342, 26100, 25432]
        balance_binance = random.choice(x)
        if msg.text.isdigit():
            if int(msg.text) >= 15000:
                async with state.proxy() as data:
                    data['count'] = msg.text
                if balance_binance >= 15000 and balance_binance > int(msg.text):
                    await binance_db.update_balance(msg.from_id, balance_binance, float(msg.text))
                    deposit = await balance.get_balance(msg.from_id)
                    await users.set_status("25000", msg.from_id)
                    await balance.insert_balance_history(msg.from_id, int(msg.text), "Личный аккаунт", "Личный аккаунт")
                    text = await users.get_text('Успешное пополнение', language[4])
                    text = text.replace('{баланс}', f'{balance_binance}').replace('{депозит}', f'{deposit[1]}')
                    await msg.answer(text)
                else:
                    text = await users.get_text('Ошибка пополнения #1', language[4])
                    text = text.replace('{сумма}', f"{int(msg.text) - int(balance_binance)}")
                    await msg.answer(text)
            else:
                deposit = await balance.get_balance(msg.from_id)
                if int(deposit[1]) + int(msg.text) >= 15000:
                    if int(balance_binance) >= int(msg.text):
                        await binance_db.update_balance(msg.from_id, balance_binance, float(msg.text))
                        await users.set_status("25000", msg.from_id)
                        await balance.insert_balance_history(
                            msg.from_id, int(msg.text), "Личный аккаунт", "Личный аккаунт")
                        text = await users.get_text('Успешное пополнение', language[4])
                        text = text.replace(
                            '{баланс}', f'{balance_binance}').replace('{депозит}', f'{int(deposit[1]) + int(msg.text)}')
                        await msg.answer(text)
                    else:
                        x = int(msg.text)
                        if 15000 > int(msg.text):
                            x = 15000
                        text = await users.get_text('Ошибка пополнения #1', language[4])
                        text = text.replace('{сумма}', f"{x - int(balance_binance)}")
                        await msg.answer(text)
                else:
                    text = await users.get_text('Ошибка пополнения #2', language[4])
                    await msg.answer(text)
        else:
            text = await users.get_text('Ошибка пополнения #3', language[4])
            await msg.answer(text)
    else:
        try:
            balance_binance = await binance.get_balance(tg_id=msg.from_id)
        except AuthenticationError:
            balance_binance = None
        if balance_binance:
            if msg.text.isdigit():
                if int(msg.text) >= 15000:
                    async with state.proxy() as data:
                        data['count'] = msg.text
                    if balance_binance[0] >= 15000:
                        await binance_db.update_balance(msg.from_id, balance_binance, float(msg.text))
                        deposit = await balance.get_balance(msg.from_id)
                        await users.set_status("25000", msg.from_id)
                        await balance.insert_balance_history(msg.from_id, int(msg.text), "Личный аккаунт",
                                                             "Личный аккаунт")
                        text = await users.get_text('Успешное пополнение', language[4])
                        text = text.replace('{баланс}', f'{balance_binance[0]}').replace('{депозит}', f'{deposit[1]}')
                        await msg.answer(text)
                    else:
                        text = await users.get_text('Ошибка пополнения #1', language[4])
                        text = text.replace('{сумма}', f"{int(msg.text) - int(balance_binance[0])}")
                        await msg.answer(text)
                else:
                    deposit = await balance.get_balance(msg.from_id)
                    if int(deposit[1]) + int(msg.text) >= 15000:
                        if int(balance_binance[0]) >= int(msg.text):
                            await binance_db.update_balance(msg.from_id, balance_binance, float(msg.text))
                            await users.set_status("25000", msg.from_id)
                            await balance.insert_balance_history(msg.from_id, int(msg.text), "Личный аккаунт",
                                                                 "Личный аккаунт")
                            text = await users.get_text('Успешное пополнение', language[4])
                            text = text.replace(
                                '{баланс}', f'{balance_binance[0]}').replace('{депозит}',
                                                                             f'{int(deposit[1]) + int(msg.text)}')
                            await msg.answer(text)
                        else:
                            x = int(msg.text)
                            if 15000 > int(msg.text):
                                x = 15000
                            text = await users.get_text('Ошибка пополнения #1', language[4])
                            text = text.replace('{сумма}', f"{x - int(balance_binance[0])}")
                            await msg.answer(text)
                    else:
                        text = await users.get_text('Ошибка пополнения #2', language[4])
                        await msg.answer(text)
            else:
                text = await users.get_text('Ошибка пополнения #3', language[4])
                await msg.answer(text)
        else:
            text = await users.get_text('Ошибка пополнения #4', language[4])
            await msg.answer(text, reply_markup=await inline.main_menu(language[4], msg.from_user.id))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(refill_handler, text='refill', state="*")
    dp.register_callback_query_handler(handle_deposit_funds, text='deposit_funds')
    dp.register_callback_query_handler(handle_review_terms, text='review_terms')
    dp.register_callback_query_handler(handle_distribution, text='distribution')
    dp.register_callback_query_handler(handle_500_15000,
                                       lambda c: c.data in ['active_50', 'active_5000', 'active_15000'])
    dp.register_callback_query_handler(stabpool_terms, text='stabpool_terms')
    dp.register_callback_query_handler(handle_partners, text='partners')
    dp.register_callback_query_handler(handle_emailing_documents, text='emailing_documents')
    dp.register_callback_query_handler(handle_emailing_alias, state=BinanceAPI.alias)
    dp.register_callback_query_handler(biguser_registration, text="15000")
    dp.register_callback_query_handler(biguser_registration_step_1, state=BigUser.binance)
    dp.register_callback_query_handler(biguser_registration_step_2, state=BigUser.kyc)
    dp.register_message_handler(binanceapi_step1_msg, state=BigUser.finish)
    dp.register_message_handler(count_refill, state=Refill.count)
    dp.register_callback_query_handler(new_docs_2, state=NewDoc.docs)
    dp.register_callback_query_handler(new_docs_3, state=NewDoc.docs_2)
