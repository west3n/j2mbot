import decouple
from aiogram import Dispatcher, types
from keyboards import inline
from database import users


async def information_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_INFORMATION")
    text = "В данном разделе Вы можете повторно ознакомиться с документами ДАО. О любых изменениях в документах, " \
           "принятых по итогам голосования, мы уведомляем участников ДАО в информационных сообщениях данного бота." \
           "\n\nЗАПРЕЩЕНО публичное размещение документов DAO J2M и их пересылка любым третьим лицам." \
           "\n\nВ ближайшие дни здесь появится дополнительная полезная информация."
    if language[4] == 'EN':
        photo = decouple.config("BANNER_INFORMATION_EN")
        text = "FAQ"
    await call.message.delete()
    await call.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=inline.information_menu(language[4]))


async def about_j2m(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    text = '<b>DAO j2M</b> — это децентрализованная организация, с гибридной моделью управления, ' \
           'объединяющая технологии, ' \
           'решения, инновации и средства участников через обмен токенов, выпуск NFT и разработку ' \
           'сервисов развивающих цифровые активы. ' \
           '\n\n<b>DAO j2M</b> - мы выбрали гибридную модель управления, при которой DAO управляются как центральным ' \
           'органом, так и децентрализованной сетью смарт контрактов. ' \
           'Такой подход сочетает в себе лучшее из обоих миров, позволяя центральному органу быстро ' \
           'принимать решения, сохраняя при этом определенную степень децентрализации.' \
           '\n\n<b>DAO J2M</b> - это современные люди, видящие будущее в цифровых активах, заинтересованные в ' \
           'увеличении своих финансовых возможностей благодаря инструментам и решениям, которые DAO ' \
           'J2M исследует и практикует вместе с его участниками. ' \
           '\n\n<b>Миссия DAO J2M</b> - проявление лучших возможностей цифровой экономики для большего ' \
           'количества людей на планете. ' \
           '\n\n<b>Цель DAO J2M на 2023 год:</b> преумножение цифровых активов участников и ' \
           'самого DAO более чем на 33% ' \
           '\n\n<b>Цель DAO до 2030 года:</b> органическое развитие количества участников в DAO более 1 млн. ' \
           'человек, с общим объемом размещенных цифровых активов в DAO превышающим оценку в  1 млрд. USDT' \
           '\n\nПриглашаем вас в DAO J2M, приумножать активы и делится возможностями с теми, ' \
           'кто любит и развивает цифровую экономику.'
    if language[4] == "EN":
        text = "<b>DAO j2M</b> is a decentralized organization with a hybrid management model that brings " \
               "together technologies, solutions, innovations, and the resources of participants through " \
               "token exchange, NFT issuance, and the development of services for advancing digital assets." \
               "\n\n<b>DAO j2M</b> - we have chosen a hybrid management model where DAOs are governed by " \
               "both a central body and a decentralized network of smart contracts. This approach combines the " \
               "best of both worlds, allowing the central body to make decisions quickly while maintaining a " \
               "certain degree of decentralization.\n\n<b>DAO J2M</b> consists of forward-thinking " \
               "individuals who envision the future in digital assets and are interested in expanding " \
               "their financial opportunities through tools and solutions that DAO J2M explores and " \
               "practices together with its participants.\n\n<b>The mission of DAO J2M</b> is to unleash " \
               "the full potential of the digital economy for a larger number of people on the planet." \
               "\n\n<b>DAO J2M's goal for 2023</b> is to multiply the digital assets of its participants " \
               "and the DAO itself by more than 33%.\n\n<b>DAO's goal by 2030</b> is to organically grow " \
               "the number of participants in the DAO to over 1 million people, with a total volume of " \
               "digital assets in the DAO exceeding an estimated 1 billion USDT.\n\nWe invite you to join " \
               "DAO J2M, multiply your assets, and share opportunities with those who love and develop the " \
               "digital economy."
    await call.message.answer(text, reply_markup=inline.about_j2m_kb(language[4]))


async def company_documents(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    documents_group = [decouple.config("USER_AGREEMENT"), decouple.config("PRIVACY_POLICY"),
                       decouple.config("J2M_DAO_RULES"), decouple.config("DISCLAIMER"),
                       decouple.config("PRODUCT_USAGE_TERMS"), decouple.config("BALANCE_DOCUMENT")]
    text = "В данном разделе, вашему вниманию представлены документы, которые вы акцептовали ранее. " \
           "Благодаря им регламентируются условия и форматы взаимодействия участников и партнёров DAO " \
           "J2M как между собой, так и с используемыми сервисами, решениями и регуляторами, а также " \
           "определяется ответственность сторон и правила применения возможностей DAO."
    if language == "EN":
        documents_group = [decouple.config("USER_AGREEMENT_EN"), decouple.config("PRIVACY_POLICY_EN"),
                           decouple.config("J2M_DAO_RULES_EN"), decouple.config("DISCLAIMER_EN"),
                           decouple.config("PRODUCT_USAGE_TERMS_EN"), decouple.config("BALANCE_DOCUMENT_EN")]
        text = "In this section, we present to your attention the documents that you have previously accepted. " \
               "These documents establish the conditions and formats of interaction between the participants and " \
               "partners of DAO J2M, both among themselves and with the utilized services, solutions, and " \
               "regulators. They also define the responsibilities of the parties and the rules for " \
               "the application of DAO capabilities."
    for document in documents_group:
        await call.message.answer_document(document)
    await call.message.answer(text, reply_markup=inline.info_documents_kb(language[4]))


async def info_products(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'Раздел "Продукты" находится в разработке!'
    if language[4] == 'EN':
        text = 'The "Products" section is currently under development!'
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.information_back(language))


async def info_collaboration(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'Раздел "Сотрудничество" находится в разработке!'
    if language[4] == 'EN':
        text = 'The "Collaboration" section is currently under development!'
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.information_back(language))


async def info_news(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'Раздел "Новости" находится в разработке!'
    if language[4] == 'EN':
        text = 'The "News" section is currently under development!'
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.information_back(language))


async def info_marketing(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'Раздел "Маркетинг" находится в разработке!'
    if language[4] == 'EN':
        text = 'The "Marketing" section is currently under development!'
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.information_back(language))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(information_handler, text='information')
    dp.register_callback_query_handler(about_j2m, text='dao')
    dp.register_callback_query_handler(company_documents, text='info_documents')
    dp.register_callback_query_handler(info_products, text='info_products')
    dp.register_callback_query_handler(info_collaboration, text='info_collaboration')
    dp.register_callback_query_handler(info_news, text='info_news')
    dp.register_callback_query_handler(info_marketing, text='info_marketing')
