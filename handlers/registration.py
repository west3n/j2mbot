import datetime
import decouple
import asyncio
import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound
from database import users, referral, nft
from binance import thedex, microservice
from handlers import commands
from keyboards import inline
from handlers.commands import Registration, SmartContract, Email, generate_random_code
from handlers.google import send_email_message, sheets_connection


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
        text_1 = await users.get_text('Приветственное сообщение #1', call.data.upper())
        text_2 = await users.get_text('Приветственное сообщение #2', call.data.upper())
        document_1 = decouple.config("USER_AGREEMENT")
        privacy_policy_doc = decouple.config("PRIVACY_POLICY")
        dao_j2m_rules_doc = decouple.config("J2M_DAO_RULES")
        disclaimer_doc = decouple.config("DISCLAIMER")
        product_usage_terms_doc = decouple.config("PRODUCT_USAGE_TERMS")
        if call.data == "EN":
            document_1 = decouple.config("USER_AGREEMENT_EN")
            privacy_policy_doc = decouple.config("PRIVACY_POLICY_EN")
            dao_j2m_rules_doc = decouple.config("J2M_DAO_RULES_EN")
            disclaimer_doc = decouple.config("DISCLAIMER_EN")
            product_usage_terms_doc = decouple.config("PRODUCT_USAGE_TERMS_EN")
        await call.message.edit_text(text_1)
        documents = [document_1, privacy_policy_doc, dao_j2m_rules_doc, disclaimer_doc, product_usage_terms_doc]
        for doc in documents:
            await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
            await asyncio.sleep(1)
            await call.message.answer_document(doc)
        await call.message.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(1)
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
            try:
                await call.message.delete()
            except MessageToDeleteNotFound:
                pass
            text = await users.get_text("Приветственное сообщение #3", data.get('language'))
            await call.message.answer(text)
            await Registration.next()


async def email_message(msg: types.Message, state: FSMContext):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    language = await users.user_data(msg.from_user.id)
    if re.match(pattern, msg.text):
        code = generate_random_code()
        async with state.proxy() as data:
            await state.update_data({"email": msg.text, "code": code})
        text = await users.get_text("Подтверждение кода из email", language[4])
        text = text.replace("{здесь email}", f"{msg.text}")
        email_text = await users.get_text('Сообщение, отправляемое по email #1', language[4])
        email_text = email_text.replace("{здесь код}", f'{code}')
        await send_email_message(to=msg.text,
                                 subject="DAO J2M verification",
                                 message_text=email_text)
        await msg.answer(text)
        await Registration.next()
    else:
        text = await users.get_text('Ошибка при формате почты', language[4])
        await msg.answer(text)


async def ver_code(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if msg.text == data.get("code"):
            await msg.answer("Верификация успешно пройдена.")
            await users.insert_email(msg.from_id, data.get('email'))
            await state.set_state(SmartContract.mint_nft.state)
            language = data.get('language')
            try:
                ref_tg = await referral.get_id_from_line_1_id(msg.from_user.id)
                ref_full_name = await users.get_tg_full_name(ref_tg[0])
            except TypeError:
                ref_tg = None
            if ref_tg:
                text = await users.get_text('Сообщение, отправляемое после верификации email (реферал)', language)
                text = text.replace("{имя реферала}", f"{ref_full_name}")
                await msg.answer(text, reply_markup=inline.yesno_refill(language))
            else:
                text = await users.get_text('Сообщение, отправляемое после верификации email (нет реферала)', language)
                await msg.answer(text, reply_markup=inline.yesno_refill(language))
        else:
            text = await users.get_text('Ошибка кода верификации', data.get('language'))
            await msg.answer(text, reply_markup=inline.email_verif(data.get('language')))
            await Registration.next()


async def one_more(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    if call.data == "new_code":
        async with state.proxy() as data:
            code = generate_random_code()
            await state.update_data({"code": code})
            text = await users.get_text("Подтверждение кода из email", language[4])
            text = text.replace("{здесь email}", "")
            email_text = await users.get_text('Сообщение, отправляемое по email #1', language[4])
            email_text = email_text.replace("{здесь код}", f'{code}')
            await send_email_message(to=data.get('email'),
                                     subject="DAO J2M verification",
                                     message_text=email_text)
            await call.message.answer(text)
            await state.set_state(Registration.ver_code.state)
    if call.data == "change_email":
        text = await users.get_text('Приветственное сообщение #3', language[4])
        await call.message.answer(text)
        await state.set_state(Registration.email.state)


async def processing_registration(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == "no":
        text = await users.get_text('Уточнение ID партнёра', language[4])
        await call.message.edit_text(text)
        await state.set_state(SmartContract.new_referral.state)
    elif call.data == 'yes':
        count = await nft.check_nft_count()
        text = await users.get_text('Подтверждение участия в DAO #1', language[4])
        text_2 = await users.get_text('Подтверждение участия в DAO #2', language[4])
        text_2 = text_2.replace('{количество}', f'{555 - int(count)}')
        await call.message.edit_text(text)
        await call.message.answer(text_2, reply_markup=inline.get_nft(language[4]))
        await SmartContract.next()


async def new_referral(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    await msg.bot.send_chat_action(msg.chat.id, "typing")
    if msg.text.isdigit():
        if int(msg.text) in await users.get_all_tg_id():
            async with state.proxy() as data:
                data["line_1"] = msg.text
            # ДОБАВЛЕНИЕ РЕФЕРАЛА
            await referral.update_line_1(msg.from_user.id, data.get('line_1'))
            try:
                text = f"Пользователь {msg.from_id} - {msg.from_user.full_name if msg.from_user.username is None else '@' + msg.from_user.username} " \
                       f"зарегистрировался по вашей партнерской программе!"
                await msg.bot.send_message(chat_id=int(data.get('line_1')),
                                           text=text)
            except:
                pass
            user_name = await users.get_tg_full_name(data.get('line_1'))
            count = await nft.check_nft_count()
            text = await users.get_text('Подтверждение ID пригласителя', language[4])
            text_2 = await users.get_text('Подтверждение участия в DAO #1', language[4])
            text_3 = await users.get_text('Подтверждение участия в DAO #2', language[4])
            text_3 = text_3.replace('{количество}', f'{555 - int(count)}')
            await msg.answer(text)
            await msg.bot.send_chat_action(msg.chat.id, "typing")
            await asyncio.sleep(1)
            await msg.answer(text_2)
            await msg.bot.send_chat_action(msg.chat.id, "typing")
            await asyncio.sleep(1)
            await msg.answer(text_3, reply_markup=inline.get_nft(language[4]))
            await state.set_state(SmartContract.start_minting.state)
        else:
            text = await users.get_text('Ошибка ввода ID пригласителя #1', language[4])
            await msg.answer(text)
    else:
        text = await users.get_text('Ошибка ввода ID пригласителя #2', language[4])
        await msg.delete()
        await msg.answer(text)


async def mint_nft(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    language = await users.user_data(call.from_user.id)
    count = await nft.check_nft_count()
    summ = 48
    if count <= 555:
        summ = 8.5
    invoiceId = await thedex.create_invoice(summ, int(call.from_user.id), "Покупка NFT")
    purse, amount = await thedex.pay_invoice('USDT_TRON', invoiceId)
    if "." in amount:
        amount = amount.replace(".", ",")
    await nft.create_nft(call.from_user.id, invoiceId)
    text = f"Для регистрации в DAO и получения NFT отправьте на указанный адрес {amount} USDT TRC\-20:" \
           f"\n\n`{purse}`" \
           "\n\nОбновить и ознакомится со статусом транзакции Вы можете с помощью кнопок ниже\." \
           "\n\nДля продолжения нажмите на кнопку 'Обновить'"
    if language[4] == "EN":
        text = f"To register in the DAO and receive the NFT, please send {amount} USDT TRC\-20 to " \
               f"the provided address: \n\n`{purse}`" \
               "\n\nYou can update and check the status of your transaction using the buttons below\."
    await call.message.edit_text(text, parse_mode=types.ParseMode.MARKDOWN_V2,
                                 reply_markup=inline.check_nft_status(language[4]))


async def nft_refresh(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    invoiceId = await nft.check_nft_status(call.from_user.id)
    status, title = await thedex.invoice_one(invoiceId[5])
    ads = await nft.get_ad_status(call.from_user.id)
    try:
        ads = ads[0]
    except TypeError:
        ads = None
    if ads == "Реклама":
        video = decouple.config("NFT_ANIMATION")
        invitor = await referral.get_id_from_line_1_id(call.from_user.id)
        try:
            invitor = invitor[0]
        except TypeError:
            invitor = 32591016
        try:
            resp, private_key, address = await microservice.microservice_(call.from_user.id, invitor)
            dao = await nft.update_nft(call.from_user.id, address, private_key, "Successful")
        except TypeError:
            resp = None
            address = None
            private_key = None
            dao = None
        if resp:
            email_ad = await users.check_email(call.from_user.id)
            invite_link = await call.bot.create_chat_invite_link(chat_id=decouple.config('J2M_CHAT'))
            text = await users.get_text('Успешная покупка NFT (1000)', language[4])
            text = text.replace('{номер}', f'{dao[0]}').replace('{ссылка}', f'{invite_link.invite_link}')
            email_text = await users.get_text('Успешная покупка NFT (email)', language[4])
            email_text = email_text.replace('{номер}', f'{dao[0]}').replace("{адрес}", f'{address}').replace(
                "{ключ}", f'{private_key}')
            if language[4] == "EN":
                video = decouple.config("NFT_ANIMATION_EN")
            await send_email_message(to=email_ad[0],
                                     subject="DAO J2M Smart Contract",
                                     message_text=email_text)
            await call.message.answer_video(video=video,
                                            caption=text,
                                            reply_markup=inline.main_menu_short(language[4]))
            await call.bot.send_message(
                chat_id=decouple.config('GROUP_ID'),
                text=f"Пользователь {call.from_user.id} - {call.from_user.username} получил NFT (РЕКЛАМА)"
                     f"\n\nПодробнее по ссылке: http://89.223.121.160:8000/admin/app/nft/")
            sh = await sheets_connection()
            worksheet_name = "NFT"
            worksheet = sh.worksheet(worksheet_name)
            worksheet.append_row((datetime.datetime.now().date().strftime("%Y-%m-%d"),
                                  call.from_user.id, "РЕКЛАМА"))
        else:
            text = await users.get_text('Ошибка покупки NFT', language[4])
            await call.message.answer(text, reply_markup=inline.main_menu_short(language[4]))
    else:
        if status == "Waiting":
            text = await users.get_text('Статус Waiting у NFT', language[4])
            await call.message.answer(text, reply_markup=inline.check_nft_status(language[4]))
        elif status == "Unpaid":
            text = await users.get_text('Статус Unpaid у NFT', language[4])
            await call.message.answer(text)
            await nft.delete_error(call.from_user.id)
        elif status == "Successful":
            video = decouple.config("NFT_ANIMATION")
            invitor = await referral.get_id_from_line_1_id(call.from_user.id)
            try:
                invitor = invitor[0]
            except TypeError:
                invitor = 32591016
            try:
                resp, private_key, address = await microservice.microservice_(call.from_user.id, invitor)
                dao = await nft.update_nft(call.from_user.id, address, private_key, "Successful")
            except TypeError:
                resp = None
                address = None
                private_key = None
                dao = None
            if resp:
                email_ad = await users.check_email(call.from_user.id)
                invite_link = await call.bot.create_chat_invite_link(chat_id=decouple.config('J2M_CHAT'))
                text = await users.get_text('Успешная покупка NFT (1000)', language[4])
                text = text.replace('{номер}', f'{dao[0]}').replace('{ссылка}', f'{invite_link.invite_link}')
                email_text = await users.get_text('Успешная покупка NFT (email)', language[4])
                email_text = email_text.replace('{номер}', f'{dao[0]}').replace("{адрес}", f'{address}').replace(
                    "{ключ}", f'{private_key}')
                if language[4] == "EN":
                    video = decouple.config("NFT_ANIMATION_EN")
                await send_email_message(to=email_ad[0],
                                         subject="DAO J2M Smart Contract",
                                         message_text=email_text)
                await call.message.answer_video(video=video,
                                                caption=text,
                                                reply_markup=inline.main_menu_short(language[4]))
                await call.bot.send_message(
                    chat_id=decouple.config('GROUP_ID'),
                    text=f"Пользователь {call.from_user.id} - {call.from_user.username} купил NFT"
                         f"\n\nПодробнее по ссылке: http://89.223.121.160:8000/admin/app/nft/")
                sh = await sheets_connection()
                worksheet_name = "NFT"
                worksheet = sh.worksheet(worksheet_name)
                worksheet.append_row((datetime.datetime.now().date().strftime("%Y-%m-%d"),
                                      call.from_user.id, "Successful"))
            else:
                text = await users.get_text('Ошибка покупки NFT', language[4])
            await call.message.answer(text, reply_markup=inline.main_menu_short(language[4]))
        elif status == "Rejected":
            text = await users.get_text('Статус Rejected у NFT', language[4])
            await call.message.answer(text)
            await nft.delete_error(call.from_user.id)


async def nft_detail(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    invoiceId = await nft.check_nft_status(call.from_user.id)
    status, purse, curr, amount, title = await thedex.invoice_one_2(invoiceId[5])
    text = f"Cумма к оплате: {amount} USDT-20\n" \
           f"Кошелек для оплаты: {purse}"
    if language[4] == "EN":
        text = f"The payment amount is: {amount} USDT-20\n"
        f"Wallet for payment: {purse}"
    await call.message.answer(text, reply_markup=inline.check_nft_status(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(language_handler, state=Registration.language)
    dp.register_callback_query_handler(handle_user_terms_kb, state=Registration.accept)
    dp.register_callback_query_handler(finish_registration, state=Registration.finish)
    dp.register_message_handler(email_message, state=Registration.email)
    dp.register_message_handler(ver_code, state=Registration.ver_code)
    dp.register_callback_query_handler(one_more, state=Registration.one_more)
    dp.register_callback_query_handler(processing_registration, state=SmartContract.mint_nft)
    dp.register_message_handler(new_referral, state=SmartContract.new_referral)
    dp.register_callback_query_handler(mint_nft, state=SmartContract.start_minting)
    dp.register_callback_query_handler(nft_refresh, text="refresh_nft")
    dp.register_callback_query_handler(nft_detail, text="transaction_details_nft")
