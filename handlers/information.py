import decouple

from aiogram import Dispatcher, types
from aiogram.utils.exceptions import MessageToDeleteNotFound
from database import users, nft, balance
from keyboards import inline


async def information_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_INFORMATION")
    text = await users.get_text('Информация главное меню', language[4])
    if language[4] == 'EN':
        photo = decouple.config("BANNER_INFORMATION_EN")
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    await call.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=inline.information_menu(language[4]))


async def about_j2m(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('О DAO J2M (информация)', language[4])
    await call.message.answer(text, reply_markup=inline.about_j2m_kb(language[4]))


async def company_documents(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Документы (информация)', language[4])
    documents_group = [decouple.config("USER_AGREEMENT"), decouple.config("PRIVACY_POLICY"),
                       decouple.config("J2M_DAO_RULES"), decouple.config("DISCLAIMER"),
                       decouple.config("PRODUCT_USAGE_TERMS"), decouple.config("BALANCE_DOCUMENT")]
    if language[4] == "EN":
        documents_group = [decouple.config("USER_AGREEMENT_EN"), decouple.config("PRIVACY_POLICY_EN"),
                           decouple.config("J2M_DAO_RULES_EN"), decouple.config("DISCLAIMER_EN"),
                           decouple.config("PRODUCT_USAGE_TERMS_EN"), decouple.config("BALANCE_DOCUMENT_EN")]
    for document in documents_group:
        await call.message.answer_document(document)
    await call.message.answer(text, reply_markup=inline.info_documents_kb(language[4]))


async def info_products(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Продукты (информация)', language[4])
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.info_products_kb(language[4]))


async def info_bot_nft(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'info_dao_bot':
        text = await users.get_text('О боте DAO J2М (информация)', language[4])
    else:
        text = await users.get_text('NFT (информация)', language[4])
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.info_bot_nft_kb(language[4]))


async def info_collaboration(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'dao_partners':
        await call.answer('Раздел находится в разработке.')
    else:
        text = await users.get_text('Сотрудничество (информация)', language[4])
        await call.message.delete()
        await call.message.answer(text, reply_markup=inline.info_collaboration_kb(language))


async def info_news(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    count_nft = await nft.check_nft_count()
    count_nft_7days = await nft.check_nft_count_last_7_days()
    common_pool = await balance.count_pool()
    common_pool_7days = await balance.count_balance_history_7_days()
    text = await users.get_text("Новости (информация)", language[4])
    text = text.replace("{участники}", str(count_nft))
    text = text.replace("{пул}", str(common_pool))
    text = text.replace("{участники 7 дней}", str(count_nft_7days))
    text = text.replace("{пул 7 дней}",
                        f"🆙 +{str(common_pool_7days)}" if common_pool_7days > 0 else f"🔽 {str(common_pool_7days)}")
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.info_news_kb(language[4]))


async def info_marketing(call: types.CallbackQuery):
    if call.data in ['gloss', 'product_pres', 'partners_pres', 'instructions',
                     'online_resources', 'webinars', 'visuals']:
        await call.answer('Раздел находится в разработке.')
    else:
        language = await users.user_data(call.from_user.id)
        text = await users.get_text('Маркетинг (информация)', language[4])
        await call.message.delete()
        await call.message.answer(text, reply_markup=inline.info_marketing_kb(language))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(information_handler, text='information')
    dp.register_callback_query_handler(about_j2m, text='dao')
    dp.register_callback_query_handler(company_documents, text='info_documents')
    dp.register_callback_query_handler(info_products, text='info_products')
    dp.register_callback_query_handler(info_bot_nft, lambda c: c.data in ['info_dao_bot', 'info_nft'])
    dp.register_callback_query_handler(info_collaboration, lambda c: c.data in ['info_collaboration', 'dao_partners'])
    dp.register_callback_query_handler(info_news, text='info_news')
    dp.register_callback_query_handler(
        info_marketing, lambda c: c.data in ['info_marketing', 'gloss', 'product_pres', 'partners_pres', 'instructions',
                                             'online_resources', 'webinars', 'visuals'])
