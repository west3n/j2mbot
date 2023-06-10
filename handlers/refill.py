import asyncio
import os

import decouple
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards import inline
from database import users, documents, referral
import shutup

shutup.please()


class DocsAccept(StatesGroup):
    accept = State()
    finish = State()
    referral = State()
    new_referral = State()


class BigUser(StatesGroup):
    binance = State()
    kyc = State()
    contract = State()


async def refill_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_REFILL")
    if not await documents.status_docs(call.from_user.id):
        text = "Для продолжения вам нужно прочесть и " \
               "подтвердить 'Правила DAO J2M', 'Дисклеймер' и 'Правила использования продуктов'"
        text_2 = "После ознакомления с присланными документами, пожалуйста, подтвердите согласие с условиями."
        dao_j2m_rules_doc = decouple.config("J2M_DAO_RULES")
        disclaimer_doc = decouple.config("DISCLAIMER")
        product_usage_terms_doc = decouple.config("PRODUCT_USAGE_TERMS")
        if language[4] == 'EN':
            photo = decouple.config("BANNER_REFILL_EN")
            text = "To continue, you need to read and confirm the 'DAO J2M Rules', " \
                   "'Disclaimer' and 'Product Usage Terms'."
            text_2 = "After reviewing the documents sent, please confirm your agreement to the terms."
            dao_j2m_rules_doc = decouple.config("J2M_DAO_RULES_EN")
            disclaimer_doc = decouple.config("DISCLAIMER_EN")
            product_usage_terms_doc = decouple.config("PRODUCT_USAGE_TERMS_EN")
        await call.message.delete()
        mess = await call.message.answer_photo(
            photo=photo,
            caption=text)
        await call.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(2)
        await call.message.answer_document(dao_j2m_rules_doc)
        await call.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(1)
        await call.message.answer_document(disclaimer_doc)
        await call.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(1)
        await call.message.answer_document(product_usage_terms_doc)
        await call.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(4)
        await call.bot.delete_message(chat_id=call.message.chat.id,
                                      message_id=mess.message_id)
        await call.message.answer(text_2, reply_markup=inline.user_docs(language[4]))
        await DocsAccept.accept.set()
    else:
        call.data = "15000"
        await biguser_registration(call)


async def docs_complete(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    async with state.proxy() as data:
        await call.message.edit_reply_markup(reply_markup=inline.user_docs_2(language[4]))
        await DocsAccept.next()


async def finish_docs(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    async with state.proxy() as data:
        if call.data == "docs_accept":
            language = await users.user_data(call.from_user.id)
            await call.message.edit_reply_markup(reply_markup=inline.user_docs(language[4]))
            await state.set_state(DocsAccept.accept.state)
        else:
            await call.message.delete()
            try:
                ref_tg = await referral.get_id_from_line_1_id(call.from_user.id)
                ref_full_name = await users.get_tg_full_name(ref_tg[0])
            except TypeError:
                ref_tg = None
            if ref_tg:
                text = f"<b>DAO J2M</b> является сообществом," \
                       f"которое подразумевает взаимодействие между его участниками.\n\n" \
                       f"Прежде чем Вы воспользуетесь любым из наших предложений," \
                       f" мы просим Вас подтвердить, что информацией о возможности участия в DAO" \
                       f" с вами поделился/лась: <b>{ref_full_name}</b>.\n\n" \
                       f"<em>После этого подтверждения изменить данную информацию будет нельзя</em>"
                if language[4] == "EN":
                    text = f"<b>DAO J2M</b> is a community," \
                           f"which occurs among its members.\n\n" \
                           f"Before you take advantage of our offers", \
                        f" we ask you to check that the information about the possibility of participating in the DAO" \
                        f"shared/became: <b>{ref_full_name}</b>.\n\n" \
                        f"<em>After this confirmation, it will be impossible to change the illustration</em>"
                await call.message.answer(text, reply_markup=inline.yesno_refill(language[4]))
            else:
                text = f"<b>DAO J2M</b> является сообществом ….. " \
                       f"которое подразумевает взаимодействие между его участниками.\n\n" \
                       f"Прежде чем Вы воспользуетесь любым из наших предложений," \
                       f" мы просим Вас подтвердить, что информацию о возможности участия в DAO " \
                       f"вы получили самостоятельно.\n\n" \
                       f"<em>После этого подтверждения изменить данную информацию будет нельзя</em>"
                if language[4] == "EN":
                    text = f"<b>DAO J2M</b> is a community" \
                           f"which implies interaction between its participants.\n\n" \
                           f"Before you use any of our offers," \
                           f" we ask you to confirm that the information about the possibility of participating in " \
                           f"the DAO " \
                           f"you got yourself.\n\n" \
                           f"<em>After this confirmation, you will not be able to change this information</em>"
                await call.message.answer(text, reply_markup=inline.yesno_refill(language[4]))
            await documents.add_approve_docs(call.from_user.id)
            await DocsAccept.next()


async def processing_refill(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == "no":
        text = "Уточните ID пользователя, который вас пригласил и отправьте его сообщением"
        if language[4] == 'EN':
            text = "Please provide the user ID of the person who invited you and send it via message."
        await call.message.edit_text(text)
        await state.set_state(DocsAccept.new_referral.state)
    elif call.data == 'yes':
        text = "Выберите один вариант:"
        if language[4] == "EN":
            text = "Please select one option:"
        await call.message.edit_text(text, reply_markup=inline.refill_account(language[4]))


async def new_referral(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    await msg.bot.send_chat_action(msg.chat.id, "typing")
    if msg.text.isdigit():
        if int(msg.text) in await users.get_all_tg_id():
            async with state.proxy() as data:
                data["line_1"] = msg.text
            await referral.update_line_1(msg.from_user.id, data.get('line_1'))
            user_name = await users.get_tg_full_name(data.get('line_1'))
            text = f"Данные успешно сохранены! \n\n" \
                   f"Вы указали в качестве пригласившего вас пользователя <b>{user_name}</b>"
            text_2 = "Выберите один вариант:"
            if language[4] == 'EN':
                text = f"The data has been successfully saved!\n\n"
                f"You have indicated <b>{user_name}</b> as the user who invited you."
                text_2 = "Please select one option:"
            await msg.answer(text)
            await state.finish()
            await msg.bot.send_chat_action(msg.chat.id, "typing")
            await asyncio.sleep(2)
            await msg.answer(text_2, reply_markup=inline.refill_account(language[4]))
        else:
            text = f"Данный пользователь не зарегистрирован в системе!\n\n" \
                   f"<em> Если вы не знаете эти цифры, уточните у пользователя (Раздел Реферальная программа)</em>"
            if language[4] == 'EN':
                text = f"This user is not registered in the system!\n\n"
                f"<em>If you don't know these digits, please clarify with the user (Referral Program section).</em>"
            await msg.answer(text)
    else:
        text = "Пожалуйста, укажите уникальный идентификатор пользователя цифрами.\n\n" \
               "<em> Если вы не знаете эти цифры, уточните у пользователя (Раздел Реферальная программа)</em>"
        if language[4] == "EN":
            text = "Please provide a unique user identifier using digits.\n\n<em>If you don't know this information, " \
                   "please ask the user (Referral Program section) for clarification</em>"
        await msg.delete()
        await msg.answer(text)


async def biguser_registration(call: types.CallbackQuery):
    if await documents.check_contract(call.from_user.id) is None:
        language = await users.user_data(call.from_user.id)
        text = 'Для того, чтобы воспользоваться данным предложением, необходимо:\n\n' \
               '- Заключить договор\n- Настроить субаккаунт\n- Подключить торгового бота'
        text_2 = 'Зарегистрирован ли у Вас аккаунт на бирже Binance?'
        if language[4] == "EN":
            text = "To take advantage of this offer, you need to:\n\n" \
                   "- Sign a contract\n- Set up a subaccount\n- Connect the trading bot."
            text_2 = "Do you have an account registered on the Binance exchange?"
        await call.message.delete()
        mess = await call.message.answer(text)
        await call.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(1)
        await call.message.answer(text_2, reply_markup=inline.yesno(language[4]))
        await asyncio.sleep(3)
        await call.bot.delete_message(call.from_user.id, mess.message_id)
        await BigUser.binance.set()
    else:
        pass


async def biguser_registration_step_1(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'no':
        text = 'Чтобы воспользоваться данным предложением Вам необходимо зарегистрировать аккаунт ' \
               'на бирже Binance и пройти KYC верификацию, ' \
               'после этого вы сможете продолжить процедуру регистрации в программе ' \
               'управляемых субаккаунтов.'
        if language[4] == "EN":
            text = "To take advantage of this offer, you need to register an account on the Binance exchange " \
                   "and complete the KYC verification process. After that, you can proceed with the registration " \
                   "procedure in the managed sub-accounts program."
        await call.message.edit_text(text, reply_markup=inline.main_menu(language[4]))
        await state.finish()
    else:
        text = 'Пройдена ли у Вас KYC верификация?'
        if language[4] == "EN":
            text = "Have you completed the KYC verification?"
        await call.message.edit_text(text, reply_markup=inline.yesno(language[4]))
        await BigUser.next()


async def biguser_registration_step_2(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'no':
        text = 'Чтобы воспользоваться данным предложением Вам необходимо зарегистрировать аккаунт на бирже Binance' \
               ' и пройти KYC верификацию, после этого вы сможете продолжить процедуру ' \
               'регистрации в программе управляемых субаккаунтов.'
        if language[4] == "EN":
            text = "To take advantage of this offer, you need to register an account on the Binance exchange " \
                   "and complete the KYC verification process. After that, you can proceed with the registration " \
                   "procedure in the managed sub-accounts program."
        await call.message.edit_text(text, reply_markup=inline.main_menu(language[4]))
        await state.finish()
    else:
        text = 'Ознакомьтесь с договором, скачайте его, заполните все поля отмеченные желтым цветом, ' \
               'поменяйте цвет выделения текста на белый, ' \
               'распечатайте и подпишите. Отправьте нам заполненный договор без подписи ' \
               'в электронном виде и фото, либо скан подписанного документа в виде файла!'
        contract = decouple.config("CONTRACT")
        if language[4] == "EN":
            text = "Please review the contract, download it, fill in all the fields marked in yellow, " \
                   "change the text highlight color to white, print it out, and sign it. Send us the " \
                   "completed contract without the signature in electronic format and a " \
                   "photo or scan of the signed document."
            contract = decouple.config("CONTRACT_EN")
        await call.message.delete()
        await call.message.answer(text)
        await call.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(2)
        await call.message.answer_document(contract)
        await call.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(2)
        text_2 = "Мы передадим его в Binance. Через 4 рабочих дня Binance оповестит Вас по электронной почте о том, " \
                 "что Вам доступен функционал управляемых субсчетов\n" \
                 "После получения уведомления от Binance, Вам нужно совершить следующие шаги:\n\n" \
                 "Зайдите в свой профиль (иконка Вашего профиля вверху справа)\n." \
                 "В открывшемся меню, снизу появился раздел “Субаккаунты”\n" \
                 "Слева в меню раздела нажмите “Управляемый субаккаунт” Будьте внимательны, не спутав его с разделом " \
                 "“Управление аккаунтом”\nОткроется страница настройки управляемых субаккаунтов. В правом верхнем " \
                 "углу нажмите на кнопку “Создать управляемый субаккаунт”\n." \
                 "Появится окно создания субаккаунта.\n" \
                 "Нужно ввести название счета. Название счёта должно быть написано латинскими буквами и содержать " \
                 "ваши Имя и Фамилию. Данная информация нужна, чтобы наши технические специалисты могли " \
                 "идентифицировать Вас в клиентской базе.\nУказываете наш UID: 476589212 и наш email: " \
                 "cfo@sainatools.com\nСистема запросит подтверждение операции. " \
                 "После подтверждения система присвоит субсчету виртуальный адрес электронной почты (alias), " \
                 "который будет начинаться с указанного Вами ранее nickname.\n\nПодробная инструкция " \
                 "по <a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera-saina-instrukciya'>ссылке</a>"
        if language[4] == "EN":
            text_2 = "We will transfer it to Binance. In 4 business days, Binance will notify you by email that " \
                     "you have access to managed sub-accounts functionality.\n After receiving the notification " \
                     "from Binance, you need to follow these steps:\n\n" \
                     " Go to your profile (icon of your profile at the top right).\n" \
                     "In the opened menu, you will see the 'Subaccounts' section at the bottom.\n" \
                     "Click on 'Managed Subaccount' in the left menu of the section. Please be careful not to " \
                     "confuse it with the 'Account Management' section.\n" \
                     "The page for managing managed sub-accounts will open. In the top right corner, " \
                     "click on the 'Create Managed Subaccount' button. \nA subaccount creation window will appear.\n" \
                     "Enter the account name. The account name should be written in Latin letters and include your " \
                     "first and last name. This information is needed for our technical " \
                     "specialists to identify you in the client database.\nSpecify our UID: 476589212 and " \
                     "our email: cfo@sainatools.com.\nThe system will request confirmation of the operation. " \
                     "After confirmation, the system will assign a virtual email address (alias) to the sub-account, " \
                     "which will start with the nickname you provided earlier.\n\nDetailed instructions are available at " \
                     "this <a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera-saina-instrukciya'>" \
                     "link</a>."
        await call.message.answer(text_2)
        await BigUser.next()


async def biguser_registration_step3(message: types.Message, state: FSMContext):

    language = await users.user_data(message.from_user.id)
    if message.document:
        user_id = message.from_user.id
        text = "Договор отправлен на проверку"
        if language[4] == "EN":
            text = "The contract has been sent"
        folder_name = f'Договор_{user_id}'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        file_name = os.path.join(folder_name, message.document.file_name)
        await message.document.download(file_name)
        await message.reply(text)
        await message.bot.send_chat_action(message.chat.id, "typing")
        await asyncio.sleep(3)
    else:
        text = "Нужно отправить документы или скриншоты в виде файла!\n\n" \
                             "Попробуйте еще раз."
        if language[4] == "EN":
            text = "You need to send documents or screenshots as a file!\n\n" \
                   "Try again."
        await message.answer(text)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(refill_handler, text='refill')
    dp.register_callback_query_handler(docs_complete, state=DocsAccept.accept)
    dp.register_callback_query_handler(finish_docs, state=DocsAccept.finish)
    dp.register_callback_query_handler(processing_refill, state=DocsAccept.referral)
    dp.register_message_handler(new_referral, state=DocsAccept.new_referral)
    dp.register_callback_query_handler(biguser_registration, text="15000")
    dp.register_callback_query_handler(biguser_registration_step_1, state=BigUser.binance)
    dp.register_callback_query_handler(biguser_registration_step_2, state=BigUser.kyc)
    dp.register_message_handler(biguser_registration_step3, content_types=['text', 'video', 'photo', 'document'],
                                state=BigUser.contract)
