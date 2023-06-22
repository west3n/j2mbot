import decouple
import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import users, referral, nft
from binance import thedex, microservice
from handlers import commands
from keyboards import inline
from handlers.commands import Registration, SmartContract


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
        text_1 = "Спасибо за ваш интерес к нашей Децентрализованной Автономной Организации (ДАО/DAO J2M)." \
                 "\n\nМы создали этого бота, чтобы упростить доступ к нашей деятельности. Перед тем, как " \
                 "предоставить Вам возможность стать участником DAO, мы хотели бы ознакомить вас с несколькими " \
                 "важными документами и условиями участия в нашем DAO." \
                 "\n\nЭти документы обеспечивают прозрачность, безопасность и конфиденциальность для всех участников." \
                 "\n\nНаш бот отправит Вам несколько документов, которые необходимо изучить и акцептировать." \
                 "\n\n1. Пользовательское соглашение: Этот документ описывает правила и обязанности, которые вы" \
                 " принимаете при использовании бота нашего ДАО и связанных с ним услуг. Он включает в себя общие " \
                 "правила поведения, ограничения и юридические аспекты." \
                 "\n\n2. Политика конфиденциальности: Мы ценим вашу конфиденциальность и защиту ваших личных данных." \
                 " В этом документе мы описываем, какие данные мы собираем, как мы их используем и какие меры" \
                 " безопасности мы принимаем." \
                 "\n\n3. Правила ДАО: Данный документ является основным руководством для участников нашего ДАО." \
                 " В нем описываются правила взаимодействия, процесс управления и важные аспекты, связанные с " \
                 "участием в наших активностях." \
                 "\n\n4. Дисклеймер: Данный документ содержит важную информацию о рисках, связанных с " \
                 "использованием бота нашего ДАО и участием в наших активностях." \
                 "\n\n5. Правила использования продуктов: В рамках нашего ДАО мы предоставляем доступ к " \
                 "программному обеспечению наших партнеров. Перед использованием этих продуктов, рекомендуется " \
                 "внимательно ознакомиться с правилами и условиями их использования." \
                 "\n\nУчастие в нашем ДАО предоставит вам возможность внести свой вклад в развитие " \
                 "возможностей цифровой экономики, участвовать в совместных решениях в рамках нашей организации." \
                 "\n\nПожалуйста, внимательно изучите документы, прежде чем принимать их условия." \
                 "\n\nЕсли Вы принимаете условия описанные в документах ДАО, нажмите на кнопку 'Принимаю'" \
                 "\n\nЕсли у вас возникнут вопросы или потребуется дополнительная информация, не стесняйтесь " \
                 "обратиться к нашей поддержке. Мы всегда готовы помочь вам в процессе присоединения к нашему ДАО." \
                 "\n\nЖелаем вам взаимовыгодного участия в нашем DAO J2M!"
        text_2 = "Принимаете условия, указанные в документах?"
        document_1 = decouple.config("USER_AGREEMENT")
        privacy_policy_doc = decouple.config("PRIVACY_POLICY")
        dao_j2m_rules_doc = decouple.config("J2M_DAO_RULES")
        disclaimer_doc = decouple.config("DISCLAIMER")
        product_usage_terms_doc = decouple.config("PRODUCT_USAGE_TERMS")
        if call.data == 'en':
            text_1 = "Thank you for your interest in our Decentralized Autonomous Organization (DAO J2M)." \
                     "\n\nWe have created this bot to facilitate access to our activities. Before granting" \
                     " you the opportunity to become a participant in our DAO, we would like to familiarize you " \
                     "with some important documents and terms of participation in our DAO." \
                     "\n\nThese documents ensure transparency, security, and confidentiality for all participants." \
                     "\n\nOur bot will send you several documents that you need to review and accept:" \
                     "\n\n1. User Agreement: This document describes the rules and obligations you accept when using " \
                     "our DAO's bot and related services. It includes general code of conduct, limitations, " \
                     "and legal aspects." \
                     "\n\n2. Privacy Policy: We value your privacy and the protection of your personal data. " \
                     "In this document, we describe what data we collect, how we use it, and the security " \
                     "measures we take." \
                     "\n\n3. DAO Rules: This document serves as the main guide for participants in our DAO. " \
                     "It outlines the rules of interaction, governance process, and important aspects related " \
                     "to participating in our activities." \
                     "\n\n4. Disclaimer: This document contains important information about the risks associated " \
                     "with using our DAO's bot and participating in our activities." \
                     "\n\n5. Product Terms of Use: Within our DAO, we provide access to software products from our" \
                     " partners. Before using these products, it is recommended to carefully review their terms and " \
                     "conditions of use." \
                     "\n\nParticipating in our DAO will give you the opportunity to contribute to the development " \
                     "of digital economy possibilities and participate in collaborative decision-making within " \
                     "our organization." \
                     "\n\nPlease carefully review the documents before accepting their terms." \
                     "\n\nIf you agree to the conditions described in the DAO documents, " \
                     "click on the 'Accept' button.\n\nIf you have any questions or need additional information, " \
                     "feel free to reach out to our support. We are always ready to assist you in the process of " \
                     "joining our DAO." \
                     "\n\nWe wish you a mutually beneficial participation in our DAO J2M!"
            text_2 = "Do you accept the terms specified in the documents?"
            document_1 = decouple.config("USER_AGREEMENT_EN")
            privacy_policy_doc = decouple.config("PRIVACY_POLICY_EN")
            dao_j2m_rules_doc = decouple.config("J2M_DAO_RULES_EN")
            disclaimer_doc = decouple.config("DISCLAIMER_EN")
            product_usage_terms_doc = decouple.config("PRODUCT_USAGE_TERMS_EN")
        await call.message.edit_text(text_1)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(1)
        await call.message.answer_document(document_1)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(1)
        await call.message.answer_document(privacy_policy_doc)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(1)
        await call.message.answer_document(dao_j2m_rules_doc)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(1)
        await call.message.answer_document(disclaimer_doc)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(1)
        await call.message.answer_document(product_usage_terms_doc)
        await call.message.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(2)
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
            await state.set_state(SmartContract.mint_nft.state)
            await users.add_new_user(call.from_user.id, call.from_user.username,
                                     call.from_user.full_name, data.get('language'))
            # await commands.bot_start_call(call)
            language = data.get('language')
            try:
                ref_tg = await referral.get_id_from_line_1_id(call.from_user.id)
                ref_full_name = await users.get_tg_full_name(ref_tg[0])
            except TypeError:
                ref_tg = None
            if ref_tg:
                text = f"Мы стремимся создать сообщество, основанное на взаимодействии и сотрудничестве между нашими " \
                       f"участниками.\n\n" \
                       f"Согласно нашим правилам, которые Вы приняли, прежде чем вы сможете воспользоваться всеми " \
                       f"возможностями, " \
                       f"предоставляемыми нашим ДАО, мы просим Вас подтвердить, что информация о возможности " \
                       f"присоединиться к нашему сообществу была передана вам от " \
                       f"{ref_full_name}. Это обеспечивает дополнительный уровень доверия и помогает нам подтвердить " \
                       f"вашу легитимность в нашем ДАО.\n\n" \
                       f"Примечание: После данного подтверждения изменение этой информации будет невозможным, " \
                       f"поскольку на следующем этапе регистрации эти данные будут внесены в смарт-контракт ДАО."
                if language == "EN":
                    text = f"We strive to create a community based on interaction and collaboration among our " \
                           f"members.\n\n" \
                           f"According to our rules, which you have accepted before you can take advantage of all the " \
                           f"opportunities" \
                           f"provided by our DAO, we kindly ask you to confirm that the information about the possibility of " \
                           f"joining" \
                           f"our community was passed to you by {ref_full_name}. This ensures an additional level of trust " \
                           f"and helps us" \
                           f"confirm your legitimacy in our DAO.\n\n" \
                           f"Note: After this confirmation, it will be impossible to change this information, as in the next " \
                           f"registration stage, these data will be entered into the DAO smart contract."
                await call.message.answer(text, reply_markup=inline.yesno_refill(language))
            else:
                text = f"Мы стремимся создать сообщество, основанное на взаимодействии и сотрудничестве между нашими " \
                       f"участниками.\n\n" \
                       f"Согласно нашим правилам, которые Вы приняли, прежде чем вы сможете воспользоваться всеми " \
                       f"возможностями, " \
                       f"предоставляемыми нашим ДАО, мы просим Вас подтвердить, что информация о возможности " \
                       f"присоединиться к нашему сообществу была найдена самостоятельно. Это обеспечивает " \
                       f"дополнительный уровень доверия и помогает нам подтвердить " \
                       f"вашу легитимность в нашем ДАО.\n\n" \
                       f"Примечание: После данного подтверждения изменение этой информации будет невозможным, " \
                       f"поскольку на следующем этапе регистрации эти данные будут внесены в смарт-контракт ДАО."
                if language == "EN":
                    text = f"We strive to create a community based on interaction and collaboration among our members.\n\n"
                    f"According to our rules, which you have accepted, before you can take advantage of all the opportunities "
                    f"provided by our DAO, we kindly ask you to confirm that the information about the possibility of joining "
                    f"our community was found independently by you. This ensures an additional level of trust and helps us "
                    f"confirm your legitimacy in our DAO.\n\n"
                    f"Note: After this confirmation, it will be impossible to change this information, as in the next "
                    f"registration stage, these data will be entered into the DAO smart contract."
                await call.message.edit_text(text, reply_markup=inline.yesno_refill(language))


async def processing_registration(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == "no":
        text = "Уточните у того, кто Вас пригласил его ID участника ДАО и отправьте нам этот номер."
        if language[4] == 'EN':
            text = "Please clarify with the person who invited you for their " \
                   "DAO participant ID and send us that number."
        await call.message.edit_text(text)
        await state.set_state(SmartContract.new_referral.state)
    elif call.data == 'yes':
        count = await nft.check_nft_count()
        text = "Вы приняли условия работы с DAO J2M! Теперь, чтобы официально стать участником и получить " \
               "полный доступ к нашим возможностям и привилегиям, вам необходимо приобрести NFT (невзаимозаменяемый" \
               " токен), который будет служить подтверждением вашего участия в нашем ДАО." \
               "\n\nNFT является уникальным цифровым активом, зарегистрированным в блокчейне. Приобретение этого " \
               "токена позволит нам записать в смарт контракт информацию о вашем статусе участника и о том, " \
               "кто вас пригласил. Это поможет нам подтвердить вашу легитимность в нашем ДАО и обеспечить " \
               "прозрачность взаимодействия между участниками. " \
               "\n\nПриобретение NFT участия имеет несколько преимуществ:" \
               "\n- Возможность принимать активное участие в жизни нашего сообщества." \
               "\n- Различные привилегии и вознаграждения для участников." \
               "\n- Доступ к таким преимуществам, которые включают в себя эксклюзивную возможности " \
               "использовать ПО наших партнеров, образовательный контент и многое другое." \
               "\n- Идентификация Вас как участника ДАО" \
               "\n- Прозрачность и надежность в работе нашего сообщества." \
               "\n\nСпасибо за ваше понимание и готовность принять участие в нашем ДАО! Мы рады " \
               "приветствовать вас в нашем активном и развивающемся сообществе!"
        text_2 = "В рамках нашего ДАО мы предлагаем особое преимущество первым 555 участникам. " \
                 "Они могут приобрести NFT всего за 5 USDT (US Dollar Tether)!" \
                 "\n\nЭто уникальная возможность стать частью нашего ДАО на более выгодных условиях. " \
                 "NFT участия не только даст вам полный доступ к нашим активностям, но и откроет двери к ряду " \
                 "привилегий, вознаграждений и участию в развитии нашего сообщества." \
                 "\n\nПосле распределения первых 555 NFT, право участия в ДАО можно будет приобрести за  50 USDT." \
                 "\n\nУ Вас есть возможность стать одним из первых участников нашего ДАО и воспользоваться " \
                 f"преимуществами этого предложения! Осталось {555 - int(count)} NFT за 1 USDT."
        if language[4] == "EN":
            text = "You have accepted the terms of working with DAO J2M! Now, to officially become a participant " \
                   "and gain full access to our capabilities and privileges, you need to acquire an NFT " \
                   "(non-fungible token), which will serve as confirmation of your participation in our DAO." \
                   "\n\nAn NFT is a unique digital asset registered on the blockchain. Acquiring this token " \
                   "will allow us to record information about your participant status and who invited you in a " \
                   "smart contract. This will help us verify your legitimacy in our DAO and ensure transparency " \
                   "of interactions among participants.\n\nAcquiring the participation NFT has several advantages:" \
                   "\n- The opportunity to actively participate in our community's life." \
                   "\n- Various privileges and rewards for participants." \
                   "\n- Access to exclusive benefits, including the use of our partners' software, educational " \
                   "content, and more.\n- Identification of you as a DAO participant." \
                   "\n- Transparency and reliability in the operation of our community." \
                   "\n\nThank you for your understanding and willingness to participate in our DAO! " \
                   "We are delighted to welcome you to our active and growing community!"
            text_2 = "As part of our DAO, we offer a special advantage to the first 555 participants. " \
                     "They can acquire the NFT for only 5 USDT (US Dollar Tether)!" \
                     "\n\nThis is a unique opportunity to become part of our DAO on more favorable terms. " \
                     "The participation NFT will not only grant you full access to our activities but also " \
                     "open doors to a range of privileges, rewards, and participation in the development of " \
                     "our community.\n\nAfter the distribution of the first 555 NFTs, the right to participate " \
                     "in the DAO can be acquired for 50 USDT.\n\nYou have the opportunity to become one of the " \
                     "first participants in our DAO and take advantage of this offer! " \
                     f"There are {555 - int(count)} NFTs left for 1 USDT."
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
            await referral.update_line_1(msg.from_user.id, data.get('line_1'))
            user_name = await users.get_tg_full_name(data.get('line_1'))
            count = await nft.check_nft_count()
            text = f"Данные успешно сохранены! \n\n" \
                   f"Вы указали в качестве пригласившего вас пользователя <b>{user_name}</b>"
            text_2 = "Вы приняли условия работы с DAO J2M! Теперь, чтобы официально стать участником и получить " \
                     "полный доступ к нашим возможностям и привилегиям, вам необходимо приобрести NFT (невзаимозаменяемый" \
                     " токен), который будет служить подтверждением вашего участия в нашем ДАО." \
                     "\n\nNFT является уникальным цифровым активом, зарегистрированным в блокчейне. Приобретение этого " \
                     "токена позволит нам записать в смарт контракт информацию о вашем статусе участника и о том, " \
                     "кто вас пригласил. Это поможет нам подтвердить вашу легитимность в нашем ДАО и обеспечить " \
                     "прозрачность взаимодействия между участниками. " \
                     "\n\nПриобретение NFT участия имеет несколько преимуществ:" \
                     "\n- Возможность принимать активное участие в жизни нашего сообщества." \
                     "\n- Различные привилегии и вознаграждения для участников." \
                     "\n- Доступ к таким преимуществам, которые включают в себя эксклюзивную возможности " \
                     "использовать ПО наших партнеров, образовательный контент и многое другое." \
                     "\n- Идентификация Вас как участника ДАО" \
                     "\n- Прозрачность и надежность в работе нашего сообщества." \
                     "\n\nСпасибо за ваше понимание и готовность принять участие в нашем ДАО! Мы рады " \
                     "приветствовать вас в нашем активном и развивающемся сообществе!"
            text_3 = "В рамках нашего ДАО мы предлагаем особое преимущество первым 555 участникам. " \
                     "Они могут приобрести NFT всего за 5 USDT (US Dollar Tether)!" \
                     "\n\nЭто уникальная возможность стать частью нашего ДАО на более выгодных условиях. " \
                     "NFT участия не только даст вам полный доступ к нашим активностям, но и откроет двери к ряду " \
                     "привилегий, вознаграждений и участию в развитии нашего сообщества." \
                     "\n\nПосле распределения первых 555 NFT, право участия в ДАО можно будет приобрести за  50 USDT." \
                     "\n\nУ Вас есть возможность стать одним из первых участников нашего ДАО и воспользоваться\n " \
                     f"преимуществами этого предложения! Осталось {555 - int(count)} NFT за 5 USDT."
            if language[4] == 'EN':
                text = f"The data has been successfully saved!\n\n"
                f"You have indicated <b>{user_name}</b> as the user who invited you."
                text_2 = "You have accepted the terms of working with DAO J2M! Now, to officially become a participant " \
                         "and gain full access to our capabilities and privileges, you need to acquire an NFT " \
                         "(non-fungible token), which will serve as confirmation of your participation in our DAO." \
                         "\n\nAn NFT is a unique digital asset registered on the blockchain. Acquiring this token " \
                         "will allow us to record information about your participant status and who invited you in a " \
                         "smart contract. This will help us verify your legitimacy in our DAO and ensure transparency " \
                         "of interactions among participants.\n\nAcquiring the participation NFT has several advantages:" \
                         "\n- The opportunity to actively participate in our community's life." \
                         "\n- Various privileges and rewards for participants." \
                         "\n- Access to exclusive benefits, including the use of our partners' software, educational " \
                         "content, and more.\n- Identification of you as a DAO participant." \
                         "\n- Transparency and reliability in the operation of our community." \
                         "\n\nThank you for your understanding and willingness to participate in our DAO! " \
                         "We are delighted to welcome you to our active and growing community!"
                text_3 = "As part of our DAO, we offer a special advantage to the first 555 participants. " \
                         "They can acquire the NFT for only 5 USDT (US Dollar Tether)!" \
                         "\n\nThis is a unique opportunity to become part of our DAO on more favorable terms. " \
                         "The participation NFT will not only grant you full access to our activities but also " \
                         "open doors to a range of privileges, rewards, and participation in the development of " \
                         "our community.\n\nAfter the distribution of the first 555 NFTs, the right to participate " \
                         "in the DAO can be acquired for 50 USDT.\n\nYou have the opportunity to become one of the " \
                         "first participants in our DAO and take advantage of this offer! " \
                         f"There are {555 - int(count)} NFTs left for 5 USDT."
            await msg.answer(text)
            await msg.bot.send_chat_action(msg.chat.id, "typing")
            await asyncio.sleep(1)
            await msg.answer(text_2)
            await msg.bot.send_chat_action(msg.chat.id, "typing")
            await asyncio.sleep(1)
            await msg.answer(text_3, reply_markup=inline.get_nft(language[4]))
            await state.set_state(SmartContract.start_minting.state)
        else:
            text = f"Данный пользователь не зарегистрирован в системе!\n\n" \
                   f"<em> Если вы не знаете эти цифры, уточните у пользователя (Раздел Реферальная программа)</em>"
            if language == 'EN':
                text = f"This user is not registered in the system!\n\n"
                f"<em>If you don't know these digits, please clarify with the user (Referral Program section).</em>"
            await msg.answer(text)
    else:
        text = "Пожалуйста, укажите уникальный идентификатор пользователя цифрами.\n\n" \
               "<em> Если вы не знаете эти цифры, уточните у пользователя (Раздел Реферальная программа)</em>"
        if language == "EN":
            text = "Please provide a unique user identifier using digits.\n\n<em>If you don't know this information, " \
                   "please ask the user (Referral Program section) for clarification</em>"
        await msg.delete()
        await msg.answer(text)


async def mint_nft(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    language = await users.user_data(call.from_user.id)
    count = await nft.check_nft_count()
    summ = 48
    if count <= 555:
        summ = 3.475
    invoiceId = await thedex.create_invoice(summ, int(call.from_user.id), "Покупка NFT")
    purse, amount = await thedex.pay_invoice('USDT_TRON', invoiceId)
    if "." in amount:
        amount = amount.replace(".", ",")
    await nft.create_nft(call.from_user.id, invoiceId)
    text = f"Для регистрации в DAO и получения NFT отправьте на указанный адрес {amount} USDT TRC\-20:" \
           f"\n\n`{purse}`" \
           "\n\nОбновить и ознакомится со статусом транзакции Вы можете с помощью кнопок ниже\."
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
    status = await thedex.invoice_one(invoiceId[5])
    if status == "Waiting":
        text = "Нужно еще немного времени на проверку, пожалуйста, повторите позже"
        if language[4] == "EN":
            text = "Further time is needed for verification. Please try again later."
        await call.message.answer(text, reply_markup=inline.check_nft_status(language[4]))

    elif status == "Unpaid":
        text = "Вы не успели оплатить. Процедуру необходимо провести заново\n\n"
        if language[4] == "EN":
            text = "You missed the payment deadline. The procedure needs to be repeated.\n\n"
        await call.message.answer(text)
        await nft.delete_error(call.from_user.id)

    elif status == "Successful":
        animation = decouple.config("NFT_ANIMATION")
        invitor = await referral.get_id_from_line_1_id(call.from_user.id)
        try:
            invitor = invitor[0]
        except TypeError:
            invitor = 1
        try:
            resp, private_key, address = await microservice.microservice_(call.from_user.id, invitor)
            dao = await nft.update_nft(call.from_user.id, address, private_key, "Successful")
        except TypeError:
            resp = None
            address = None
            private_key = None
            dao = None
        if resp:
            text = f"Транзакция прошла успешно!" \
                   f"\n\nПоздравляем с приобретением NFT участия в нашем ДАО!" \
                   f"\nВаш индивидуальный номер участника DAO: {dao}" \
                   f"\nТеперь вам доступен полный функционал бота." \
                   f"\n\nВы стали частью нашей активной и развивающейся организации. Ваш NFT будет служить " \
                   f"подтверждением вашего статуса и прав в рамках нашего ДАО." \
                   f"\n\nВместе мы выбираем устойчивые решения по увеличению своих цифровых активов, " \
                   f"создаем будущее и осознанно используем современные технологии. Удачи в Вашем дальнейшем " \
                   f"развитии совместно с DAO J2M!" \
                   f"\n\nNFT хранится на защищенном кошельке созданном специально для вас. " \
                   f"\nАдрес кошелька с NFT: {address}" \
                   f"\nПриватный ключ: {private_key}" \
                   f"\n\nВ дальнейшем Вы сможете перевести её на любой другой ваш кошелек. " \
                   f"Подробнее об этом Вы узнаете в разделе 'Информация'"
            if language[4] == "EN":
                text = f"Transaction completed successfully!" \
                       f"\n\nCongratulations on acquiring the participation NFT in our DAO!" \
                       f"\nYour unique DAO participant number is {dao}.\nYou now have full access to the " \
                       f"bot functionality.\n\nYou have become part of our active and growing organization. " \
                       f"Your NFT will serve as confirmation of your status and rights within our DAO." \
                       f"\n\nTogether, we choose sustainable solutions to increase our digital assets, " \
                       f"create the future, and consciously utilize modern technologies. " \
                       f"Best of luck in your further development alongside DAO J2M!" \
                       f"\n\nYour NFT is stored in a secure wallet created specifically for you. " \
                       f"\nWallet address with NFT: {address}" \
                       f"\nPrivate key: {private_key}" \
                       f"\n\nIn the future, you will be able to transfer it to any other wallet of yours. " \
                       f"You can find more information about this in the 'Information' section."
            await call.message.answer_animation(animation=animation,
                                                caption=text,
                                                reply_markup=inline.main_menu_short(language[4]))
        else:

            text = "Произошла ошибка, обратитесь в поддержку"
            if language[4] == "EN":
                text = "An error occurred. Please contact support."
        await call.message.answer(text, reply_markup=inline.main_menu_short(language[4]))
    elif status == "Rejected":
        text = "Произошла ошибка. Деньги вернуться к вам на счет."
        if language[4] == "EN":
            text = "An error occurred. The money will be refunded to your account."
        await call.message.answer(text)
        await nft.delete_error(call.from_user.id)


async def nft_detail(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    invoiceId = await nft.check_nft_status(call.from_user.id)
    status, purse, curr, amount = await thedex.invoice_one_2(invoiceId[5])
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
    dp.register_callback_query_handler(processing_registration, state=SmartContract.mint_nft)
    dp.register_message_handler(new_referral, state=SmartContract.new_referral)
    dp.register_callback_query_handler(mint_nft, state=SmartContract.start_minting)
    dp.register_callback_query_handler(nft_refresh, text="refresh_nft")
    dp.register_callback_query_handler(nft_detail, text="transaction_details_nft")
