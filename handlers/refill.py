import asyncio
import os
import re
import decouple
import shutup

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import handlers.refill_500
from keyboards import inline
from database import users, documents, referral, binance_db, balance
from binance import actions as binance

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
    finish = State()


class BinanceAPI(StatesGroup):
    alias = State()
    api_key = State()
    api_secret = State()


class Refill(StatesGroup):
    count = State()


async def refill_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_REFILL")
    x = await documents.status_docs(call.from_user.id)
    status = await users.check_status(call.from_user.id)
    try:
        status = status[0]
    except TypeError:
        status = None
    try:
        x = x[0]
    except TypeError:
        x = False
    if status is None:
        if x is False:
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
            call.data = "yes"
            await step_2_common(call)
    else:
        await handlers.refill_500.registration_500(call)


async def docs_complete(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
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
        await state.finish()
        text = "Выберите один вариант:"
        if language[4] == "EN":
            text = "Please select one option:"
        await call.message.edit_text(text, reply_markup=inline.refill_account(language[4]))


async def step_2_common(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    x = await documents.check_contract(call.from_user.id)
    try:
        x = x[0]
        if x == "":
            x = None
    except TypeError:
        x = None
    if x is None:
        text = "Выберите один вариант:"
        if language[4] == "EN":
            text = "Please select one option:"
        await call.message.delete()
        await call.message.answer(text, reply_markup=inline.refill_account(language[4]))
    else:
        await biguser_registration(call)


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
    x = await documents.check_contract(call.from_user.id)
    try:
        x = x[0]
        if x == "":
            x = None
    except TypeError:
        x = None
    if x is None:
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
        await asyncio.sleep(3)
        await call.bot.delete_message(call.from_user.id, mess.message_id)
        await call.message.answer(text_2, reply_markup=inline.yesno(language[4]))
        await BigUser.binance.set()
    else:
        await binanceapi_step1_call(call)


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
                 "по <a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera-" \
                 "saina-instrukciya'>ссылке</a>\n\n" \
                 "Обратите внимание! Документов не может быть менее двух! Отправьте заполненый документ " \
                 "и документ с подписью в одном сообщении!"

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
                     "which will start with the nickname you provided earlier.\n\n" \
                     "Detailed instructions are available at this <a href='https://teletype.in/@lmarket/" \
                     "podkluchenie-subakkaunta-sonera-saina-instrukciya'>link</a>."
        await call.message.answer(text_2)
        await BigUser.next()


async def biguser_registration_step3(message: types.Message, state: FSMContext):
    language = await users.user_data(message.from_user.id)
    if message.document:
        user_id = message.from_user.id
        folder_name = f'Договор_{user_id}'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        file_name = os.path.join(folder_name, message.document.file_name)
        await message.document.download(file_name)
        async with state.proxy() as data:
            if 'document_count' not in data:
                data['document_count'] = 0
                data['document_path'] = ''
            data['document_count'] += 1
            data['document_path'] += f"http://89.223.121.160:8000/files/bot/{file_name}\n"
        await BigUser.next()
    else:
        text = "Нужно отправить документы или скриншоты в виде файла!\n\n" \
               "Попробуйте еще раз."
        if language[4] == "EN":
            text = "You need to send documents or screenshots as a file!\n\n" \
                   "Try again."
        await message.answer(text)

    async with state.proxy() as data:
        if 'document_count' in data and data['document_count'] == 1:
            text = "Документы успешно сохранены! "
            if language[4] == "EN":
                text = "Documents successfully saved! Wait for administrator confirmation!"
            await documents.save_contract_path(data.get('document_path'), message.from_user.id)
            await message.answer(text)
            await state.finish()
            await binanceapi_step1_msg(message)
        else:
            await documents.save_contract_path(data.get('document_path'), message.from_user.id)


async def binanceapi_step1_msg(message: types.Message):
    x = await documents.check_approve_contract(message.from_id)
    if x is True:
        language = await users.user_data(message.from_user.id)
        text = "Чтобы мы могли активировать торговлю на вашем аккаунте, " \
               "отправьте нам присвоенный системой адрес почты (alias) ответным сообщением.\n\n" \
               "Подробная инструкция " \
               "по <a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera-" \
               "saina-instrukciya'>ссылке</a>"

        if language[4] == "EN":
            text = "To enable trading on your account, please send us the email address (alias) assigned by the " \
                   "system in a reply message.\n\nDetailed instructions are available at the following " \
                   "<a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera-saina-instrukciya'>link</a>."
        await message.answer(text)
        await BinanceAPI.alias.set()
    else:
        pass


async def binanceapi_step1_call(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    y = await documents.check_approve_contract(call.from_user.id)
    if y is True:
        x = await binance_db.check_binance_keys(call.from_user.id)
        try:
            x = x[0]
        except TypeError:
            x = None
        if not x:
            await call.message.delete()
            text = "Чтобы мы могли активировать торговлю на вашем аккаунте, " \
                   "отправьте нам присвоенный системой адрес почты (alias) ответным сообщением.\n\n" \
                   "Подробная инструкция " \
                   "по <a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera-" \
                   "saina-instrukciya'>ссылке</a>"

            if language[4] == "EN":
                text = "To enable trading on your account, please send us the email address (alias) assigned by the " \
                       "system in a reply message.\n\nDetailed instructions are available at the following " \
                       "<a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera-saina-instrukciya'>link</a>."
            await call.message.answer(text)
            await BinanceAPI.alias.set()
        else:
            await main_refill_menu(call)
    else:
        await call.message.delete()
        text = "Администратор еще проверяет ваши договор, пожалуйста ожидайте!"
        if language[4] == "EN":
            text = "The administrator is still reviewing your contracts, please wait!"
        await call.message.answer(text)


async def binanceapi_step2(msg: types.Message):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    language = await users.user_data(msg.from_user.id)
    if re.match(pattern, msg.text):
        await users.insert_alias(msg.text, msg.from_id)
        text = "Нам потребуется один рабочий день для его активации.\n" \
               "После подтверждения нами, что счет настроен, и за один рабочий день до запуска, " \
               "наш сотрудник свяжется с Вами, и оповестит Вас, что спот-счет управляемого " \
               "субаккаунта можно пополнить и сообщить нам точную сумму.\n\n" \
               "Мы сможем перевести ее внутри вашего счета Бинанс на торговлю фьючерсами." \
               "После того, как наши специалисты активируют Ваш субаккаунт, в разделе управляемых субаккаунтов," \
               " рядом с созданным аккаунтом у Вас появится зеленая галочка под пунктом “Фьючерсы”. " \
               "Для пополнения субаккаунта нажмите “Перевести”\n\n" \
               "Ответным сообщением пришлите в бота <b>API KEY</b>\n\n" \
               "<a href='https://www.binance.com/ru/support/faq/%D0%BA%D0%B0%D0%BA-" \
               "%D1%81%D0%BE%D0%B7%D0%B4%D0%B0%D0%B2%D0%B0%D1%82%D1%8C-api-%D0%BA%D0%BB%D1%8E%D1%87%D0%B8-" \
               "%D0%BD%D0%B0-binance-360002502072'>" \
               "Как получить API KEY?</a>"
        if language[4] == "EN":
            text = "We will need one business day to activate it. Once we confirm that the account is set up, " \
                   "our representative will contact you one business day before the launch to inform you that " \
                   "you can fund the managed sub-account and provide us with the exact amount.\n\nWe will be " \
                   "able to transfer it within your Binance account for futures trading. After our specialists " \
                   "activate your sub-account, you will see a green checkmark next to the 'Futures' option in " \
                   "the Managed Sub-accounts section. To fund your sub-account, click on 'Transfer'." \
                   "\n\nPlease send the <b>API KEY</b> in a reply message to the bot.\n\n" \
                   "<a href='https://www.binance.com/en/support/faq/how-to-create-api-keys-on-binance-360002502072'>" \
                   "How to obtain API KEY?</a>"
        await msg.answer(text)
        await BinanceAPI.next()
    else:
        text = "Попробуйте ввести корректный e-mail."
        if language[4] == "EN":
            text = "Please try entering a valid email address."
        await msg.answer(text)


async def binance_step3(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['api_key'] = msg.text
    text = "Пришлите <b>API Secret</b>\n\n" \
           "<a href='https://www.binance.com/ru/support/faq/%D0%BA%D0%B0%D0%BA-" \
           "%D1%81%D0%BE%D0%B7%D0%B4%D0%B0%D0%B2%D0%B0%D1%82%D1%8C-api-%D0%BA%D0%BB%D1%8E%D1%87%D0%B8-" \
           "%D0%BD%D0%B0-binance-360002502072'>" \
           "Как получить API SECRET?</a>"
    if language[4] == "EN":
        text = "Please provide the <b>API Secret</b>.\n\n" \
               "<a href='https://www.binance.com/en/support/faq/how-to-create-api-keys-on-binance-360002502072'>" \
               "How to obtain API SECRET?</a>"
    await msg.answer(text)
    await BinanceAPI.next()


async def binance_step4(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['api_secret'] = msg.text
        credentials_valid = binance.check_credentials(data.get('api_key'), data.get('api_secret'))
    if credentials_valid is True:
        text = "Данные успешно сохранены!"
        if language[4] == "EN":
            text = "The data has been successfully saved!"
        await msg.answer(text, reply_markup=inline.continue_refill(language[4]))
        await binance_db.save_binance_keys(msg.from_user.id, data.get('api_key'), data.get('api_secret'))
        await state.finish()
    else:
        text = f"Api Key: <em>{data.get('api_key')}</em> и Secret Key: <em>{data.get('api_secret')} " \
               f"недействительны.</em>\nПопробуйте еще раз. Введите Api Key:\n\n" \
               f"<a href='https://www.binance.com/ru/support/faq/%D0%BA%D0%B0%D0%BA-" \
               "%D1%81%D0%BE%D0%B7%D0%B4%D0%B0%D0%B2%D0%B0%D1%82%D1%8C-api-%D0%BA%D0%BB%D1%8E%D1%87%D0%B8-" \
               "%D0%BD%D0%B0-binance-360002502072'>" \
               "Как получить API KEY?</a>"
        if language[4] == "EN":
            text = f"Api Key: <em>{data.get('api_key')}</em> and Secret Key: <em>{data.get('api_secret')}</em>" \
                   f" are invalid.\nPlease try again. Enter the Api Key:\n\n" \
                   "<a href='https://www.binance.com/en/support/faq/how-to-create-api-keys-on-binance-360002502072'>" \
                   "How to obtain API KEY?</a>"
        await msg.answer(text)
        await state.set_state(BinanceAPI.api_key.state)


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
    balance_binance = await binance.get_balance(tg_id=msg.from_id)
    if msg.text.isdigit():
        if int(msg.text) >= 15000:
            async with state.proxy() as data:
                data['count'] = msg.text
            if balance_binance >= 15000:
                await balance.insert_deposit(msg.from_id, int(msg.text))
                deposit = await balance.get_balance(msg.from_id)
                await users.set_status("15000", msg.from_id)
                await balance.insert_balance_history(msg.from_id, int(msg.text))
                text = f"Ваш Баланс Binance: {balance_binance}\n\n" \
                       f"Пополнение выполнено успешно.\n\n" \
                       f"<b>Активный депозит J2M: {deposit[1]} USDT</b>\n\n" \
                       f"<em>Мы сообщим Вам, когда запустим торговлю, и будем держать связь с Вами. " \
                       f"Вы можете осуществлять вывод в любое время, по предварительной заявке. " \
                       f"Это необходимо для того, чтобы мы закрыли открытые ордера и " \
                       f"Вы не потеряли свою доходность.\n\n " \
                       f"Заявку необходимо подавать в чат боте, в разделе “Вывод”. " \
                       f"Мы дадим Вам рекомендацию по оптимальному моменту вывода " \
                       f"для получения максимальной доходности. " \
                       f"Срок рассмотрения заявки до 24 часов.\n\n" \
                       f"При выводе без заявки, компания оставляет за собой право отключить аккаунт от реферальной " \
                       f"и мотивационной программы с последующим баном на полгода!</em>"
                if language[4] == "EN":
                    text = f"Your Binance Balance: {balance_binance}\n\n" \
                           "Deposit successfully completed.\n\n<em>We will notify you when trading starts " \
                           "and will stay in touch with you. You can make withdrawals at any time by " \
                           "submitting a prior request. This is necessary for us to close open orders and ensure " \
                           "that you do not lose your profitability.\n\nTo make a withdrawal request, please use " \
                           "the chat bot in the 'Withdraw' section. We will provide you with a recommendation on the " \
                           "optimal timing for withdrawal to maximize your returns. " \
                           "The processing time for withdrawal " \
                           "requests is up to 24 hours.\n\nWhen making withdrawals without a request, the company " \
                           "reserves the right to disable the account from the referral and incentive program, with " \
                           "a subsequent ban for six months!</em>"
                await msg.answer(text)
            else:
                text = f"<b>Сумма на вашем аккаунте Binance не может быть меньше, чем сумма пополнения!</b>\n\n" \
                       f"<em>Для продолжения пополните аккаунт на сумму " \
                       f"{int(msg.text) - int(balance_binance)} USDT и создайте новую заявку!</em>"
                if language[4] == "EN":
                    text = ""
                await msg.answer(text)
        else:
            deposit = await balance.get_balance(msg.from_id)
            if int(deposit[1]) + int(msg.text) >= 15000:
                if int(balance_binance) >= int(msg.text):
                    await balance.insert_deposit(msg.from_id, int(msg.text))
                    await users.set_status("15000", msg.from_id)
                    await balance.insert_balance_history(msg.from_id, int(msg.text))
                    text = f"Ваш Баланс Binance: {balance_binance}\n\n" \
                           f"Пополнение выполнено успешно.\n\n" \
                           f"<b>Активный депозит J2M: {int(deposit[1]) + int(msg.text)} USDT</b>\n\n" \
                           f"<em>Мы сообщим Вам, когда запустим торговлю, и будем держать связь с Вами. " \
                           f"Вы можете осуществлять вывод в любое время, по предварительной заявке. " \
                           f"Это необходимо для того, чтобы мы закрыли открытые ордера и " \
                           f"Вы не потеряли свою доходность.\n\n " \
                           f"Заявку необходимо подавать в чат боте, в разделе “Вывод”. " \
                           f"Мы дадим Вам рекомендацию по оптимальному моменту вывода " \
                           f"для получения максимальной доходности. " \
                           f"Срок рассмотрения заявки до 24 часов.\n\n" \
                           f"При выводе без заявки, компания оставляет за собой право отключить аккаунт от " \
                           f"реферальной и мотивационной программы с последующим баном на полгода!</em>"
                    if language[4] == "EN":
                        text = f"Your Binance Balance: {balance_binance}\n\n" \
                               "Deposit successfully completed.\n\n<em>We will notify you when trading starts " \
                               "and will stay in touch with you. You can make withdrawals at any time by " \
                               "submitting a prior request. This is necessary for us to close open orders and ensure " \
                               "that you do not lose your profitability.\n\nTo make a withdrawal request, please use " \
                               "the chat bot in the 'Withdraw' section. We will provide " \
                               "you with a recommendation on the " \
                               "optimal timing for withdrawal to maximize your returns. " \
                               "The processing time for withdrawal " \
                               "requests is up to 24 hours.\n\nWhen making withdrawals without a request, the " \
                               "company reserves the right to disable the account from the referral " \
                               "and incentive program, with a subsequent ban for six months!</em>"
                    await msg.answer(text)
                else:
                    x = int(msg.text)
                    if 15000 > int(msg.text):
                        x = 15000

                    text = f"<b>Сумма на вашем аккаунте Binance не может быть меньше, чем сумма пополнения!</b>\n\n" \
                           f"<em>Для продолжения пополните аккаунт на сумму " \
                           f"{x - int(balance_binance)} USDT и создайте новую заявку!</em>"
                    if language[4] == "EN":
                        text = ""
                    await msg.answer(text)

            else:
                text = f"<b>Сумма пополнения не может быть меньше, чем 15.000 USDT!</b>"
                if language[4] == "EN":
                    text = ""
                await msg.answer(text)
    else:
        text = f"<b>Введите сумму целыми числами, без букв, запятых и прочего.</b>"
        if language[4] == "EN":
            text = ""
        await msg.answer(text)


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
    dp.register_message_handler(binanceapi_step1_msg, state=BigUser.finish)
    dp.register_message_handler(binanceapi_step2, state=BinanceAPI.alias)
    dp.register_message_handler(binance_step3, state=BinanceAPI.api_key)
    dp.register_message_handler(binance_step4, state=BinanceAPI.api_secret)
    dp.register_message_handler(count_refill, state=Refill.count)
