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
        text_2 = "Принимаете условия пользовательского соглашения?"
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
            text_2 = "Do you accept the terms of the user agreement?"
            document_1 = decouple.config("USER_AGREEMENT_EN")
            privacy_policy_doc = decouple.config("PRIVACY_POLICY_EN")
            dao_j2m_rules_doc = decouple.config("J2M_DAO_RULES_EN")
            disclaimer_doc = decouple.config("DISCLAIMER_EN")
            product_usage_terms_doc = decouple.config("PRODUCT_USAGE_TERMS_EN")
        await call.message.edit_text(text_1)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(2)
        await call.message.answer_document(document_1)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(2)
        await call.message.answer_document(privacy_policy_doc)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(2)
        await call.message.answer_document(dao_j2m_rules_doc)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(2)
        await call.message.answer_document(disclaimer_doc)
        await call.message.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(2)
        await call.message.answer_document(product_usage_terms_doc)
        await call.message.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(3)
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
