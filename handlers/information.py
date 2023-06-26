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
        reply_markup=inline.new_information_menu(language[4]))


async def distribution_menu(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = "Здесь будет информация о Распределении доходности"
    if language[4] == 'EN':
        text = "Here you will find information about the distribution of profitability"
    await call.message.delete()
    await call.message.answer(text=text,
                              reply_markup=inline.information_back(language[4]))


async def conditions_menu(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = "Здесь будут условия пополнения и вывода"
    if language[4] == 'EN':
        text = "There will be conditions for replenishment and withdrawal"
    await call.message.delete()
    await call.message.answer(text=text,
                              reply_markup=inline.information_back(language[4]))


async def urls_menu(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = "Здесь будут важные ссылки"
    if language[4] == 'EN':
        text = "Important links here"
    await call.message.delete()
    await call.message.answer(text=text,
                              reply_markup=inline.information_back(language[4]))


async def docs_menu(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = "Здесь будет документация"
    if language[4] == 'EN':
        text = "Documentation will be here"
    await call.message.delete()
    await call.message.answer(text=text,
                              reply_markup=inline.information_back(language[4]))


async def company_documents(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    documents_group = [decouple.config("USER_AGREEMENT"), decouple.config("PRIVACY_POLICY"),
                       decouple.config("J2M_DAO_RULES"), decouple.config("DISCLAIMER"),
                       decouple.config("PRODUCT_USAGE_TERMS"), decouple.config("BALANCE_DOCUMENT")]
    text = "Для возврата в главное меню, нажмите кнопку ниже"
    if language == "EN":
        documents_group = [decouple.config("USER_AGREEMENT_EN"), decouple.config("PRIVACY_POLICY_EN"),
                           decouple.config("J2M_DAO_RULES_EN"), decouple.config("DISCLAIMER_EN"),
                           decouple.config("PRODUCT_USAGE_TERMS_EN"), decouple.config("BALANCE_DOCUMENT_EN")]
        text = "To return to the main menu, please click the button below"
    for document in documents_group:
        await call.message.answer_document(document)
    await call.message.answer(text, reply_markup=inline.back_button(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(information_handler, text='information')
    dp.register_callback_query_handler(distribution_menu, text='distribution')
    dp.register_callback_query_handler(conditions_menu, text='conditions')
    dp.register_callback_query_handler(urls_menu, text='urls')
    dp.register_callback_query_handler(docs_menu, text='docs')
    dp.register_callback_query_handler(company_documents, text='company_documents')
