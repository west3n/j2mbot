import decouple
from aiogram import Dispatcher, types
from keyboards import inline
from database import users


async def information_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_INFORMATION")
    text = "Здесь вы можете изучить FAQ"
    if language[4] == 'EN':
        photo = decouple.config("BANNER_INFORMATION_EN")
        text = "FAQ"
    await call.message.delete()
    await call.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=inline.information_menu(language[4]))


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


def register(dp: Dispatcher):
    dp.register_callback_query_handler(information_handler, text='information')
    dp.register_callback_query_handler(distribution_menu, text='distribution')
    dp.register_callback_query_handler(conditions_menu, text='conditions')
    dp.register_callback_query_handler(urls_menu, text='urls')
    dp.register_callback_query_handler(docs_menu, text='docs')
