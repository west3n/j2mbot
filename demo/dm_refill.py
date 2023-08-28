import asyncio
import random
import decouple
import shutup

from aiogram.utils.exceptions import BadRequest, MessageToDeleteNotFound
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from demo import dm_inline, dm_database
from database import users, documents


shutup.please()


class DemoNewDoc(StatesGroup):
    docs = State()
    docs_2 = State()


class DemoBigUser(StatesGroup):
    binance = State()
    kyc = State()
    contract = State()
    finish = State()


class DemoBinanceAPI(StatesGroup):
    alias = State()


class DemoRefill(StatesGroup):
    count = State()


async def refill_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_REFILL")
    text = await users.get_text('Главное меню пополнения (1000)', language[4])
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    await call.message.answer_photo(photo, text, reply_markup=dm_inline.dm_refill_main_menu(language[4]))


async def handle_deposit_funds(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'Выберите один из вариантов:'
    if language[4] == "EN":
        text = 'Select at least one option:'
    await call.message.delete()
    await call.message.answer(text, reply_markup=dm_inline.dm_refill_account_2(language[4]))


async def handle_review_terms(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Дисклеймер (пополнение)', language[4])
    await call.message.delete()
    await call.message.answer(text, reply_markup=dm_inline.dm_distribution(language[4]))


async def handle_distribution(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Описание категорий (пополнение)', language[4])
    await call.message.edit_text(text, reply_markup=dm_inline.dm_refill_account_3(language[4]))


async def handle_500_15000(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'dm_active_50':
        text = await users.get_text('Описание категории 1 (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=dm_inline.dm_active_50(language[4]))
    elif call.data == 'dm_active_5000':
        text = await users.get_text('Описание категории 2 (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=dm_inline.dm_active_5000(language[4]))
    else:
        text = await users.get_text('Описание категории 3 (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=dm_inline.dm_active_15000(language[4]))


async def stabpool_terms(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Описание стабпула (пополнение)', language[4])
    await call.message.edit_text(text, reply_markup=dm_inline.stabpool_kb_dm(language[4]))


async def handle_partners(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Условия партнерской программы (пополнение)', language[4])
    text = text.replace('{этой таблице}', "<a href='https://drive.google.com/file/d/1ZhHtNpsE"
                                          "5Y8l1i5n6Mp1UtG44uOMiKnP/view?pli=1'>этой таблице.</a>")
    if language[4] == 'EN':
        text = text.replace('этой таблице', 'this table')
    await call.message.edit_text(text, reply_markup=dm_inline.dm_partners_kb(language[4]))


async def biguser_registration(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    status = await dm_database.get_demo_balance(call.from_user.id)
    if status[3] == "ДЕМО":
        await main_refill_menu(call)
    else:
        text = await users.get_text('Регистрация личного аккаунта #1', language[4])
        text_2 = await users.get_text('Регистрация личного аккаунта #2', language[4])
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        mess = await call.message.answer(text)
        await call.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(3)
        await call.bot.delete_message(call.from_user.id, mess.message_id)
        await call.message.answer(text_2, reply_markup=dm_inline.dm_yesno(language[4]))
        await DemoBigUser.binance.set()


async def new_docs(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    document = decouple.config('BALANCE_DOCUMENT')
    text = await users.get_text('Отправка приложения №1 (пополнение)', language[4])
    await call.bot.send_chat_action(chat_id=call.from_user.id, action="upload_document")
    await asyncio.sleep(2)
    await call.bot.send_document(chat_id=call.from_user.id, document=document)
    await call.message.answer(text, reply_markup=dm_inline.dm_user_terms(language[4]))
    await DemoNewDoc.docs.set()


async def new_docs_2(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=dm_inline.dm_user_terms_2(language[4]))
    await DemoNewDoc.next()


async def new_docs_3(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == "dm_terms_accept":
        await call.message.edit_reply_markup(reply_markup=dm_inline.dm_user_terms(language[4]))
        await state.set_state(DemoNewDoc.docs.state)
    else:
        await state.finish()
        await call.message.delete()
        await biguser_registration(call)


async def biguser_registration_step_1(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'dm_no':
        text = await users.get_text('KYC (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=await dm_inline.dm_main_menu(language[4]))
        await state.finish()
    else:
        text = await users.get_text('KYC (пополнение) #2', language[4])
        await call.message.edit_text(text, reply_markup=dm_inline.dm_yesno(language[4]))
        await DemoBigUser.next()


async def biguser_registration_step_2(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'dm_no':
        text = await users.get_text('KYC (пополнение)', language[4])
        await call.message.edit_text(text, reply_markup=await dm_inline.dm_main_menu(language[4]))
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
        await call.message.answer(text, reply_markup=dm_inline.dm_emailing_documents(language[4]))
        await state.finish()


async def handle_emailing_documents(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text('Оповещение администратору (пополнение)', language[4])
    try:
        await call.message.edit_text(text)
    except BadRequest:
        await call.message.delete()
        await call.message.answer(text)
    await state.finish()
    await asyncio.sleep(10)
    text = await users.get_text('Alias (пополнение)', language[4])
    text = text.replace('{ссылкa}', "<a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera"
                                    "-saina-instrukciya'>ссылке</a>")
    if language[4] == "EN":
        text = text.replace('ссылке', 'link')
    await call.message.answer(text)
    await asyncio.sleep(5)
    await binanceapi_step1_call(call)


async def binanceapi_step1_call(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    text = "Чтобы мы могли активировать торговлю на вашем аккаунте, отправьте нам присвоенный системой " \
           "<b>адрес почты (alias), а также настроенные API KEY, API SECRET</b> на почту менеджера " \
           "субаккаунтов sup.sonera@gmail.com, затем нажмите на кнопку 'Информация отправлена' и ждите " \
           "подтверждение. Подтверждение придёт вам в сообщении от бота." \
           "\n\nДля безопасности ваших данных мы не можем обрабатывать эту информацию через Телеграм." \
           "\n\n<b>ВАЖНО! Темой письма должен быть ваш юзернейм телеграма</b>\n\n" \
           "Подробная инструкция " \
           "по <a href='https://teletype.in/@lmarket/podkluchenie-subakkaunta-sonera-" \
           "saina-instrukciya'>ссылке</a>"
    if language[4] == "EN":
        text = "In order for us to activate trading on your account, please send us the " \
               "system-assigned email address (alias) and the configured API key and API secret to " \
               "the sub-account manager's email at sup.sonera@gmail.com. Afterward, click the " \
               "'Information Sent' button and wait for confirmation. The confirmation will be sent " \
               "to you in a message from the bot." \
               "\n\nFor the security of your data, we cannot process this information through Telegram." \
               "\n\n<b>IMPORTANT! The subject of the email should be your Telegram username.</b>" \
               "\n\nDetailed instructions can be found at <a href='https://teletype.in/@lmarket/podkluchenie" \
               "-subakkaunta-sonera-saina-instrukciya'>this link</a>."
    await call.message.answer(text, reply_markup=dm_inline.dm_emailing_alias(language[4]))
    await DemoBinanceAPI.alias.set()


async def handle_emailing_alias(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    text = 'Оповещение администратору отправлено, ожидайте подтверждения!'
    if language[4] == "EN":
        text = "Notification sent to the administrator. Please await confirmation!"
    await call.message.edit_text(text)
    await state.finish()
    await asyncio.sleep(10)
    text = f"<b>Администратор подтвердил ваши данные по API KEY, API SECRET, Alias</b>"
    if language == "EN":
        text = f"<b>The administrator has confirmed your API KEY, API SECRET, and Alias.</b>"
    await call.message.answer(text)
    await asyncio.sleep(3)
    await main_refill_menu(call)


async def main_refill_menu(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    text = f"<b>Введите сумму для пополнения:</b>"
    if language[4] == "EN":
        text = "Please enter the amount to deposit:"
    await call.message.answer(text)
    await DemoRefill.count.set()


async def count_refill(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    x = [15380, 15621, 15342, 16100, 15432, 15407, 15002, 15977, 15211]
    balance_binance = random.choice(x)
    if msg.text.isdigit():
        if int(msg.text) >= 15000:
            async with state.proxy() as data:
                data['count'] = msg.text
            if balance_binance >= 15000 and balance_binance > int(msg.text):
                deposit = await dm_database.get_demo_balance(msg.from_id)
                await dm_database.update_demo_personal_balance(msg.from_id, int(msg.text), balance_binance)
                await dm_database.insert_demo_balance_history(msg.from_id, int(msg.text), "IN", "Личный аккаунт")
                text = f"Ваш Баланс Binance: {balance_binance}\n\n" \
                       f"Пополнение выполнено успешно.\n\n" \
                       f"<b>Баланс</b>: {deposit[6] + int(msg.text)}"  \
                       f"\n<b>Активный депозит J2M: {deposit[7]} USDT</b>\n\n" \
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
                           "the chat bot in the 'Withdraw' section. We will provide you with a recommendation " \
                           "on the optimal timing for withdrawal to maximize your returns. " \
                           "The processing time for withdrawal " \
                           "requests is up to 24 hours.\n\nWhen making withdrawals without a request, the company" \
                           " reserves the right to disable the account from the referral and incentive program, " \
                           "with a subsequent ban for six months!</em>"
                await msg.answer(text, reply_markup=await dm_inline.dm_main_menu(language[4]))
                await state.finish()
            else:
                text = f"<b>Сумма на вашем аккаунте Binance не может быть меньше, чем сумма пополнения!</b>\n\n" \
                       f"<em>Для продолжения пополните аккаунт на сумму " \
                       f"{int(msg.text) - int(balance_binance)} USDT и создайте новую заявку!</em>"
                if language[4] == "EN":
                    text = f"<b>The amount in your Binance account cannot be less than the top-up amount!</b>\n\n" \
                           f"<em>To proceed, please top up your account with an amount of " \
                           f"{int(msg.text) - int(balance_binance)} USDT and create a new request!</em>"
                await msg.answer(text)
                await state.finish()
        else:
            deposit = await dm_database.get_demo_balance(msg.from_id)
            if int(deposit[7]) + int(msg.text) >= 15000:
                if int(balance_binance) >= int(msg.text):
                    await dm_database.update_demo_personal_balance(msg.from_id, int(msg.text), balance_binance)
                    await dm_database.insert_demo_balance_history(msg.from_id, int(msg.text), "IN", "Личный аккаунт")
                    text = f"Ваш Баланс Binance: {balance_binance}\n\n" \
                           f"Пополнение выполнено успешно.\n\n" \
                           f"<b>Баланс</b>: {deposit[6] + int(msg.text)}" \
                           f"\n<b>Активный депозит J2M: {int(deposit[7])} USDT</b>\n\n" \
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
                               "submitting a prior request. This is necessary for us to close open orders and " \
                               "ensure that you do not lose your profitability.\n\nTo make a withdrawal request, " \
                               "please use the chat bot in the 'Withdraw' section. We will provide " \
                               "you with a recommendation on the " \
                               "optimal timing for withdrawal to maximize your returns. " \
                               "The processing time for withdrawal " \
                               "requests is up to 24 hours.\n\nWhen making withdrawals without a request, the " \
                               "company reserves the right to disable the account from the referral " \
                               "and incentive program, with a subsequent ban for six months!</em>"
                    await msg.answer(text, reply_markup=await dm_inline.dm_main_menu(language[4]))
                    await state.finish()
                else:
                    x = int(msg.text)
                    if 15000 > int(msg.text):
                        x = 15000
                    text = f"<b>Сумма на вашем аккаунте Binance не может быть меньше, чем сумма пополнения!</b>" \
                           f"\n\n<em>Для продолжения пополните аккаунт на сумму " \
                           f"{x - int(balance_binance)} USDT и создайте новую заявку!</em>"
                    if language[4] == "EN":
                        text = f"<b>The amount in your Binance account cannot be less than the top-up amount!</b>" \
                               f"\n\n<em>To proceed, please top up your account with an amount of " \
                               f"{x - int(balance_binance)} USDT and create a new request!</em>"
                    await msg.answer(text)
                    await state.finish()
            else:
                text = f"<b>Сумма пополнения не может быть меньше, чем 15 000 USDT!</b>"
                if language[4] == "EN":
                    text = f"<b>The top-up amount cannot be less than 15 000 USDT!</b>"
                await msg.answer(text)
    else:
        text = f"<b>Введите сумму целыми числами, без букв, запятых и прочего.</b>"
        if language[4] == "EN":
            text = f"<b>Enter the sum in whole numbers, without letters, commas, etc.</b>"
        await msg.answer(text)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(refill_handler, text='dm_refill', state="*")
    dp.register_callback_query_handler(handle_deposit_funds, text='dm_deposit_funds')
    dp.register_callback_query_handler(handle_review_terms, text='dm_review_terms')
    dp.register_callback_query_handler(handle_distribution, text='dm_distribution')
    dp.register_callback_query_handler(stabpool_terms, text='dm_stabpool_terms')
    dp.register_callback_query_handler(handle_partners, text='dm_partners')
    dp.register_callback_query_handler(handle_500_15000,
                                       lambda c: c.data in ['dm_active_50', 'dm_active_5000', 'dm_active_15000'])
    dp.register_callback_query_handler(handle_emailing_documents, text='dm_emailing_documents')
    dp.register_callback_query_handler(handle_emailing_alias, state=DemoBinanceAPI.alias)
    dp.register_callback_query_handler(biguser_registration, text="dm_15000")
    dp.register_callback_query_handler(biguser_registration_step_1, state=DemoBigUser.binance)
    dp.register_callback_query_handler(biguser_registration_step_2, state=DemoBigUser.kyc)
    dp.register_message_handler(count_refill, state=DemoRefill.count)
    dp.register_callback_query_handler(new_docs_2, state=DemoNewDoc.docs)
    dp.register_callback_query_handler(new_docs_3, state=DemoNewDoc.docs_2)
