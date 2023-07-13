import asyncio
import random
import decouple
import shutup

from aiogram.utils.exceptions import BadRequest, MessageToDeleteNotFound
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import inline
from database import users, documents, binance_db, balance, thedex_db
from binance import actions as binance
from handlers.refill_500 import registration_500
from ccxt.base.errors import AuthenticationError

shutup.please()


class NewDoc(StatesGroup):
    docs = State()
    docs_2 = State()


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


class Refill(StatesGroup):
    count = State()


async def refill_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    trans = await thedex_db.get_transaction(call.from_user.id)
    photo = decouple.config("BANNER_REFILL")
    if not trans:
        text = 'Условия участия зависят от суммы размещенных криптоактивов. Мы рекомендуем изучить подробную ' \
               'информацию о каждом варианте, до пополнения баланса. ' \
               'Если Вы уже знаете все условия, то можете переходить к пополнению.'
        if language[4] == "EN":
            text = "The terms of participation depend on the amount of crypto assets you have deposited. " \
                   "We recommend reviewing detailed information about each option before depositing funds. " \
                   "If you are already familiar with all the terms, you can proceed with the deposit."
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        await call.message.answer_photo(photo, text, reply_markup=inline.refill_main_menu(language[4]))
    else:
        await registration_500(call)


async def handle_deposit_funds(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'Выберите один из вариантов:'
    if language[4] == "EN":
        text = 'Select at least one option:'
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.refill_account_2(language[4]))


async def handle_review_terms(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'DAO J2M предоставляет возможность своим участникам использовать IT продукт партнера Sonera.' \
           '\n\nОсновы размещения крипто активов в любых новых инструментах:' \
           '\n- осведомленность' \
           '\n- своевременность' \
           '\n- умеренный авантюризм' \
           '\n\nПрежде чем принимать решения о совершении действий с цифровыми и крипто-сервисами, ' \
           'важно изучить полную информацию о рисках и затратах, связанных с волатильностью рынков, ' \
           'формированием законодательной базы в мире и другими особенностями развивающейся цифровой экономики .' \
           '\n\nМы рекомендуем отказаться от идей брать кредиты, продавать имущество, привлекать заемные ' \
           'средства или использовать не свободные средства.' \
           '\n\nПравильно оцените цели участия, свои возможности и допустимый уровень риска.' \
           '\n\nДля большей уверенности обратитесь к нам или к своему пригласителю за консультацией.'
    if language[4] == "EN":
        text = "DAO J2M provides participants with the opportunity to utilize the software of the partner company, " \
               "Sonera.\n\nFundamentals of depositing crypto assets in any new instruments:" \
               "\n- Awareness" \
               "\n- Timeliness" \
               "\n- Moderate risk-taking" \
               "\n\nBefore making decisions regarding actions with digital and crypto services, it is " \
               "important to thoroughly understand the complete information about the risks and costs associated " \
               "with market volatility, the development of legislative frameworks worldwide, and other " \
               "aspects of the evolving digital economy.\n\nWe recommend refraining from taking loans, " \
               "selling assets, borrowing funds, or using non-free funds." \
               "\n\nProperly assess your participation goals, capabilities, and acceptable risk levels." \
               "\n\nFor greater confidence, you can reach out to us or your inviter for consultation."
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.distribution(language[4]))


async def handle_distribution(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = 'По условиям применения IT продукта, доходность рассчитывается еженедельно от результатов его работы.' \
           ' Процент дохода участника ДАО зависит от суммы его личного актива.' \
           '\n\nУчастники с личным криптоактивом от 500 USDT до 5000 USDT' \
           'получают вознаграждение в размере 40% от прибыли своего активного депозита' \
           '\n\nУчастники с личным криптоактивом от 5000 USDT до 15000 USDT' \
           'получают вознаграждение в размере 45% от прибыли своего активного депозита' \
           '\n\nУчастники с личным криптоактивом от 15000 USDT' \
           'получают вознаграждение в размере 50% от прибыли своего активного депозита собственного ' \
           'субаккаунта Binance.\n\nБолее детальные условия для какой суммы криптоактивов Вам интересны?'
    if language[4] == "EN":
        text = "According to the terms of use of the IT product, profitability is calculated on a weekly basis " \
               "based on its performance. The percentage \
               of income for a DAO participant depends on the amount of their personal asset." \
               "\n\nParticipants with a personal crypto asset ranging from 500 USDT to 5000 USDT receive a " \
               "reward of 40% of the profits from their active deposit." \
               "\n\nParticipants with a personal crypto asset ranging from 5000 USDT to 15000 USDT " \
               "receive a reward of 45% of the profits from their active deposit." \
               "Participants with a personal crypto asset of 15000 USDT or more receive a reward of 50% of the " \
               "profits from their active deposit in their own Binance sub-account." \
               "For more detailed conditions regarding specific amounts of crypto assets, please let me " \
               "know which range you are interested in."
    await call.message.edit_text(text, reply_markup=inline.refill_account_3(language[4]))


async def handle_500_15000(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'active_500':
        text = '<b>Условия формата участия от 500 USDT:</b>' \
               '\n\nПреимущества формата участия:' \
               '\n- Повышенный процент возможной доходности за счет того, что больший размер единого коллективного' \
               ' актива позволяет использовать большее количество стратегий торговых бота.' \
               '- Возможность использовать современные технологии высокочастотного алгоритмического трейдинга ' \
               'коллективно, с минимальным размещением личных активов.' \
               '\n\nПри размещении  активов от 500 USDT возможность вывода замораживается до того момента, ' \
               'пока сумма депозита не достигнет объема в 1000 USDT.' \
               '\n\nВарианты размещения активов от 1000 USDT:' \
               '\n- Холд тела на 1 месяц с минимальной прогнозируемой доходностью от 3%' \
               '\n- Холд тела на 3 месяца с минимальной  прогнозируемой доходностью от 12%' \
               '\n- Холд тела на 6 месяцев с минимальной прогнозируемой доходностью от 30%' \
               '\n\nПравила участия:' \
               '\n- Вывод процентов дохода осуществляется 1 раз в две недели.' \
               '\n- Минимальная сумма вывода 50$.' \
               '\n- Вывод в течении 24 часов. Расчетный день вывода Понедельник.' \
               '\n- Введенные средства поступают в работу раз в неделю в понедельник, в момент открытия торговой ' \
               'недели.' \
               '\n- День вывода тела депозита в соответствии с выбранным сроком холда рассчитывается с момента, ' \
               'когда криптоактив поступил в работу.' \
               '\n- Компания имеет право вернуть средства на кошелек пользователя и не взять их в работу если ' \
               'они не пройдут AML проверку.' \
               '\n\nМаксимально подробно условия написаны в Приложении No 1 к Условиям применения IT продукта, ' \
               'которое Вы акцептовали. Повторно изучить документ можно в разделе бота "Информация".'
        if language[4] == "EN":
            text = "Conditions of '500' participation format:" \
                   "\n\nAdvantages of participation format:" \
                   "\n- Increased potential profitability due to a larger size of the collective asset, allowing " \
                   "for the use of more trading bot strategies." \
                   "\n- The opportunity to collectively utilize modern high-frequency algorithmic trading " \
                   "technologies with minimal placement of personal assets." \
                   "\n\nWhen placing assets starting from 500 USDT, the withdrawal option is frozen until " \
                   "the deposit amount reaches 1000 USDT." \
                   "\n\nOptions for placing assets starting from 1000 USDT:" \
                   "\n- Hold period of 1 month with a minimum projected profitability of 3%." \
                   "\n- Hold period of 3 months with a minimum projected profitability of 12%." \
                   "\n- Hold period of 6 months with a minimum projected profitability of 30%." \
                   "\n\nParticipation rules:" \
                   "\n\n- Income percentages are withdrawn once every two weeks." \
                   "\n- Minimum withdrawal amount is $50." \
                   "\n- Withdrawals are processed within 24 hours. Withdrawal day is Monday." \
                   "\n- Deposited funds are put into operation once a week on Monday at the beginning of " \
                   "the trading week.\n- The withdrawal day for the deposit principal is calculated based on the " \
                   "chosen hold period, starting from the moment the crypto asset starts operating." \
                   "\n- The company has the right to return funds to the user's wallet and not put them into " \
                   "operation if they fail AML verification." \
                   "\n\nThe detailed conditions are described in Appendix No. 1 to the Terms of Use of the IT " \
                   "product, which you have accepted. You can review the document again in the " \
                   "'Information' section of the bot."
        await call.message.edit_text(text, reply_markup=inline.active_500(language[4]))
    elif call.data == 'active_15000':
        text = "<b>Условия формата участия от 15000 USDT:</b>" \
               "\n\nПреимущества формата участия:" \
               "\n- Минимальная прогнозируемая доходность от 3% в месяц." \
               "\n- Ваши криптоактивы находятся в Вашем постоянном доступе на Вашем субаккаунте Binance." \
               "\n- Только Вы имеете возможность пополнять и выводить активы в любой момент." \
               "\n\nПравила участия:" \
               "\n- Работа по инструкции." \
               "\n- Активация аккаунта 1 рабочая неделя (2-5 рабочих дней)." \
               "\n- Запуск партнерского ПО на Вашем субаккаунте 48 часов." \
               "\n- Расчет недельной доходности производится по воскресеньям." \
               "\n- Распределение доходности между участником программы и DAO - 50/50." \
               "\n- Участник еженедельно получает информацию о сумме доходности и размере вознаграждения в " \
               "DAO за предоставленное ПО в воскресенье и обязуется осуществить перевод в понедельник." \
               "\n- Вывод активного депозита возможен в любое время, по предварительной обязательной заявке " \
               "в этом боте.\n- Согласование момента вывода для получения максимальной доходности. Срок " \
               "рассмотрения до 24 часов.\n- При нарушении условий со стороны участника DAO, компания оставляет " \
               "за собой право отключить аккаунт от партнерской и мотивационной программы с " \
               "последующим баном на полгода." \
               "\n\n Максимально подробно условия написаны в Приложении No 1 к Условиям применения IT продукта, " \
               'которое Вы акцептовали. Повторно изучить документ можно в разделе бота "Информация".'
        if language[4] == 'EN':
            text = "Conditions of '15000' participation format:" \
                   "\n\nAdvantages of participation format:" \
                   "\n-Minimum projected profitability of 3% per month." \
                   "\n- Your crypto assets are accessible on your Binance sub-account." \
                   "\n- Only you have the ability to deposit and withdraw assets at any time." \
                   "\n\nParticipation rules:" \
                   "\n- Follow the instructions provided." \
                   "\n- Account activation takes 1 working week (2-5 working days)." \
                   "\n- Partner software is launched on your sub-account within 48 hours." \
                   "\n- Weekly profitability calculation is done on Sundays." \
                   "\n- Profit distribution between the program participant and DAO is 50/50." \
                   "\n- Participants receive information about the profitability amount and the size of the " \
                   "reward in DAO for providing the software on Sundays and are required to make the " \
                   "transfer on Monday.\n- Withdrawal of the active deposit is possible at any time, with a " \
                   "mandatory request in this bot.\n- Agreement on the withdrawal timing is necessary to maximize " \
                   "profitability. Processing time is up to 24 hours.\n- In case of violation of the conditions " \
                   "by the DAO participant, the company reserves the right to deactivate the account from the " \
                   "partner and incentive program, with subsequent banning for six months." \
                   "\n\nThe detailed conditions are described in Appendix No. 1 to the Terms of Use of the IT " \
                   "product, which you have accepted. You can review the " \
                   "document again in the 'Information' section of the bot."
        await call.message.edit_text(text, reply_markup=inline.active_15000(language[4]))


async def biguser_registration(call: types.CallbackQuery):
    first_check = await documents.check_it_product(call.from_user.id)
    second_check = await documents.check_kyc(call.from_user.id)
    language = await users.user_data(call.from_user.id)
    if first_check:
        if not second_check[0]:
            text = 'Для того, чтобы воспользоваться данным предложением, необходимо:\n\n' \
                   '1. Заключить договор\n2. Создать субаккаунт.\n3. Настроить субаккаунт' \
                   '\n4. Пополнить баланс субаккаунта.\n5. Подключить торгового бота'
            text_2 = 'Зарегистрирован ли у Вас аккаунт на бирже Binance?'
            if language[4] == "EN":
                text = "To take advantage of this offer, you need to:\n\n" \
                       "1. Sign a contract.\n2. Create a sub-account.\n3. Configure the sub-account." \
                       "\n4. Deposit funds into the sub-account.\n5. Connect the trading bot."
                text_2 = "Do you have an account registered on the Binance exchange?"
            try:
                await call.message.delete()
            except MessageToDeleteNotFound:
                pass
            mess = await call.message.answer(text)
            await call.bot.send_chat_action(call.message.chat.id, "typing")
            await asyncio.sleep(5)
            await call.bot.delete_message(call.from_user.id, mess.message_id)
            await call.message.answer(text_2, reply_markup=inline.yesno(language[4]))
            await BigUser.binance.set()
        else:
            contract = await documents.check_approve_contract(call.from_user.id)
            if contract[0] is False:
                text = 'Документы пока еще не подтверждены, ожидайте' \
                       '\nЕсли вы еще не отправили документ, заполните документ и ' \
                       'отправьте его на почту sup.daoj2m@gmail.com'
                if language[4] == "EN":
                    text = "The documents are not yet confirmed. Please wait."
                await call.message.delete()
                await call.message.answer_document(document=decouple.config("CONTRACT"), caption=text,
                                                   reply_markup=inline.emailing_documents(language[4]))
            else:
                await binanceapi_step1_call(call)
    else:
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        await new_docs(call)


async def new_docs(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    document = decouple.config('BALANCE_DOCUMENT')
    text = f"Условия участия зависят от суммы размещенных криптоактивов.\n\n" \
           f"Чтобы воспользоваться IT продуктами партнеров DAO необходимо " \
           f"изучить и подтвердить подробные условия в документе: " \
           f"Приложение No 1 к Условиям применения IT продукта."
    if language[4] == "EN":
        text = "Participation conditions depend on the amount of placed crypto assets.\n\n" \
               "To access IT products of DAO partners, it is necessary to review and confirm the detailed " \
               "conditions in the document: " \
               "Appendix No. 1 to the Terms of Application of the IT Product."
    await call.bot.send_chat_action(chat_id=call.from_user.id, action="upload_document")
    await asyncio.sleep(2)
    await call.bot.send_document(chat_id=call.from_user.id, document=document)
    await call.message.answer(text, reply_markup=inline.user_terms(language[4]))
    await NewDoc.docs.set()


async def new_docs_2(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=inline.user_terms_2(language[4]))
    await NewDoc.next()


async def new_docs_3(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == "terms_accept":
        await call.message.edit_reply_markup(reply_markup=inline.user_terms(language[4]))
        await state.set_state(NewDoc.docs.state)
    else:
        await state.finish()
        await call.message.delete()
        await documents.insert_it_product(call.from_user.id)
        await biguser_registration(call)


async def biguser_registration_step_1(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'no':
        text = 'Чтобы воспользоваться данным форматом пополнения, ' \
               'Вам необходимо зарегистрировать аккаунт на бирже Binance, ' \
               'а также пройти KYC верификацию Plus, с подтверждением адреса.' \
               '\n\nПосле этого вы сможете продолжить процедуру регистрации в программе управляемых субаккаунтов.'
        if language[4] == "EN":
            text = "To take advantage of this offer, you need to register an account on the Binance exchange " \
                   "and complete the KYC verification process. After that, you can proceed with the registration " \
                   "procedure in the managed sub-accounts program."
        await call.message.edit_text(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
        await state.finish()
    else:
        text = 'Пройдена ли у Вас KYC верификация Plus?'
        if language[4] == "EN":
            text = "Have you completed the KYC verification?"
        await call.message.edit_text(text, reply_markup=inline.yesno(language[4]))
        await BigUser.next()


async def biguser_registration_step_2(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    if call.data == 'no':
        text = 'Чтобы воспользоваться данным форматом пополнения, ' \
               'Вам необходимо зарегистрировать аккаунт на бирже Binance, ' \
               'а также пройти KYC верификацию Plus, с подтверждением адреса.' \
               '\n\nПосле этого вы сможете продолжить процедуру регистрации в программе управляемых субаккаунтов.'
        if language[4] == "EN":
            text = "To take advantage of this offer, you need to register an account on the Binance exchange " \
                   "and complete the KYC Plus verification process. After that, you can proceed with the registration" \
                   " procedure in the managed sub-accounts program."
        await call.message.edit_text(text, reply_markup=await inline.main_menu(language[4], call.from_user.id))
        await state.finish()
    else:
        text = "Изучите договор, Вам нужно скачать его, заполнить все желтые поля в нём. " \
               "После этого, распечатайте договор и подпишите его. Отправьте скан, либо фото подписанного документа " \
               "на почту sup.daoj2m@gmail.com, затем нажмите на кнопку 'Документы отправлены'" \
               " и ждите подтверждение от администратора. Подтверждение придёт вам в сообщении от бота." \
               "\n\n<b>Допустимые форматы файла</b>: JPG,PDF." \
               "\n\nОбратите внимание! Документов не может быть менее двух! " \
               "Отправьте заполненый документ и документ с подписью в одном сообщении!" \
               "<b>\n\nВАЖНО! Темой письма должен быть ваш юзернейм телеграма.</b>"
        contract = decouple.config("CONTRACT")
        if language[4] == "EN":
            text = "Please review the contract. You need to download it and fill in all the yellow fields. " \
                   "After that, print the contract, sign it, and send a scanned copy or a photo of the signed " \
                   "document, as well as the completed electronic document to our email sup.daoj2m@gmail.com, then " \
                   "press 'The documents have been sent' button and wait" \
                   "for confirmation from administrator, bot will send you message after approve." \
                   "\n\nAcceptable file formats: JPG, PDF." \
                   "<b>\n\nIMPORTANT! The subject of the email should be your Telegram username.</b>"
            contract = decouple.config("CONTRACT_EN")
        await call.message.delete()
        await call.bot.send_chat_action(call.message.chat.id, "upload_document")
        await asyncio.sleep(2)
        await call.message.answer_document(contract)
        await documents.add_approve_docs(call.from_user.id)
        await call.bot.send_chat_action(call.message.chat.id, "typing")
        await asyncio.sleep(2)
        await call.message.answer(text, reply_markup=inline.emailing_documents(language[4]))
        await state.finish()


async def handle_emailing_documents(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    text = 'Оповещение администратору отправлено, ожидайте подтверждения!'
    if language[4] == "EN":
        text = "Notification sent to the administrator. Please await confirmation!"
    try:
        await call.message.edit_text(text)
    except BadRequest:
        await call.message.delete()
        await call.message.answer(text)
    await call.bot.send_message(chat_id=decouple.config('GROUP_ID'),
                                text=f"Пользователь {call.from_user.id} - {call.from_user.username} отправил контракт "
                                     f"для проверки:"
                                     f"\n\nПодробнее по ссылке: http://89.223.121.160:8000/admin/app/documents/")
    await state.finish()


async def binanceapi_step1_msg(message: types.Message):
    x = await documents.check_approve_contract(message.from_id)
    if x is True:
        binance_keys = await binance_db.check_binance_keys(message.from_id)
        if not binance_keys:
            language = await users.user_data(message.from_user.id)
            text = "Чтобы мы могли активировать торговлю на вашем аккаунте, отправьте нам присвоенный системой " \
                   "<b>адрес почты (alias), а также настроенные api key, api secret</b> на почту менеджера " \
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
            await message.answer(text, reply_markup=inline.emailing_alias(language[4]))
            await BinanceAPI.alias.set()
        else:
            pass
    else:
        pass


async def binanceapi_step1_call(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    y = await documents.check_approve_contract(call.from_user.id)
    if y[0] is True:
        x = await binance_db.check_binance_keys(call.from_user.id)
        try:
            x = x[0]
        except TypeError:
            x = None
        if not x:
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
            await call.message.answer(text, reply_markup=inline.emailing_alias(language[4]))
            await BinanceAPI.alias.set()
        else:
            await main_refill_menu(call)
    else:
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        text = "Администратор еще проверяет ваши договор, пожалуйста ожидайте!"
        if language[4] == "EN":
            text = "The administrator is still reviewing your contracts, please wait!"
        await call.message.answer(text)


async def handle_emailing_alias(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    text = 'Оповещение администратору отправлено, ожидайте подтверждения!'
    if language[4] == "EN":
        text = "Notification sent to the administrator. Please await confirmation!"
    await call.message.edit_text(text)
    await call.bot.send_message(chat_id=decouple.config('GROUP_ID'),
                                text=f"Пользователь {call.from_user.id} - {call.from_user.username} "
                                     f"отправил API_KEY, API_SECRET, Alias на почту для проверки!"
                                     f"\n\nСоздайте запись в админ-панели: "
                                     f"http://89.223.121.160:8000/admin/app/binance/")
    await state.finish()


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
    ad = await binance_db.check_binance_keys(msg.from_id)
    if ad[1] == "Реклама":
        x = [15380, 15621, 15342, 16100, 15432]
        balance_binance = random.choice(x)
        if msg.text.isdigit():
            if int(msg.text) >= 15000:
                async with state.proxy() as data:
                    data['count'] = msg.text
                if balance_binance >= 15000:
                    await balance.insert_deposit(msg.from_id, int(msg.text))
                    deposit = await balance.get_balance(msg.from_id)
                    await users.set_status("15000", msg.from_id)
                    await balance.insert_balance_history(msg.from_id, int(msg.text), "Личный аккаунт")
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
                    await msg.answer(text)
                else:
                    text = f"<b>Сумма на вашем аккаунте Binance не может быть меньше, чем сумма пополнения!</b>\n\n" \
                           f"<em>Для продолжения пополните аккаунт на сумму " \
                           f"{int(msg.text) - int(balance_binance)} USDT и создайте новую заявку!</em>"
                    if language[4] == "EN":
                        text = f"<b>The amount in your Binance account cannot be less than the top-up amount!</b>\n\n" \
                               f"<em>To proceed, please top up your account with an amount of " \
                               f"{int(msg.text) - int(balance_binance)} USDT and create a new request!</em>"
                    await msg.answer(text)
            else:
                deposit = await balance.get_balance(msg.from_id)
                if int(deposit[1]) + int(msg.text) >= 15000:
                    if int(balance_binance) >= int(msg.text):
                        await balance.insert_deposit(msg.from_id, int(msg.text))
                        await users.set_status("15000", msg.from_id)
                        await balance.insert_balance_history(msg.from_id, int(msg.text), "Личный аккаунт")
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
                                   "submitting a prior request. This is necessary for us to close open orders and " \
                                   "ensure that you do not lose your profitability.\n\nTo make a withdrawal request, " \
                                   "please use the chat bot in the 'Withdraw' section. We will provide " \
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
                        text = f"<b>Сумма на вашем аккаунте Binance не может быть меньше, чем сумма пополнения!</b>" \
                               f"\n\n<em>Для продолжения пополните аккаунт на сумму " \
                               f"{x - int(balance_binance)} USDT и создайте новую заявку!</em>"
                        if language[4] == "EN":
                            text = f"<b>The amount in your Binance account cannot be less than the top-up amount!</b>" \
                                   f"\n\n<em>To proceed, please top up your account with an amount of " \
                                   f"{x - int(balance_binance)} USDT and create a new request!</em>"
                        await msg.answer(text)
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
    else:
        try:
            balance_binance = await binance.get_balance(tg_id=msg.from_id)
        except AuthenticationError:
            balance_binance = None
        if balance_binance:
            if msg.text.isdigit():
                if int(msg.text) >= 15000:
                    async with state.proxy() as data:
                        data['count'] = msg.text
                    if balance_binance[0] >= 15000:
                        await balance.insert_deposit(msg.from_id, int(msg.text))
                        deposit = await balance.get_balance(msg.from_id)
                        await users.set_status("15000", msg.from_id)
                        await balance.insert_balance_history(msg.from_id, int(msg.text), "Личный аккаунт")
                        text = f"Ваш Баланс Binance: {balance_binance[0]}\n\n" \
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
                               f"При выводе без заявки, компания оставляет за собой право отключить аккаунт от " \
                               f"реферальной и мотивационной программы с последующим баном на полгода!</em>"
                        if language[4] == "EN":
                            text = f"Your Binance Balance: {balance_binance[0]}\n\n" \
                                   "Deposit successfully completed.\n\n<em>We will notify you when trading starts " \
                                   "and will stay in touch with you. You can make withdrawals at any time by " \
                                   "submitting a prior request. This is necessary for us to close open orders and " \
                                   "ensure that you do not lose your profitability.\n\nTo make a withdrawal request, " \
                                   "please use the chat bot in the 'Withdraw' section. We will provide you with a " \
                                   "recommendation on the optimal timing for withdrawal to maximize your returns. " \
                                   "The processing time for withdrawal " \
                                   "requests is up to 24 hours.\n\nWhen making withdrawals without a request, the " \
                                   "company reserves the right to disable the account from the referral and incentive" \
                                   " program, with a subsequent ban for six months!</em>"
                        await msg.answer(text)
                    else:
                        text = f"<b>Сумма на вашем аккаунте Binance не может быть меньше, чем сумма пополнения!</b>" \
                               f"\n\n<em>Для продолжения пополните аккаунт на сумму " \
                               f"{int(msg.text) - int(balance_binance[0])} USDT и создайте новую заявку!</em>"
                        if language[4] == "EN":
                            text = f"<b>The amount in your Binance account cannot be less than the top-up amount!</b>" \
                                   f"\n\n<em>To proceed, please top up your account with an amount of " \
                                   f"{int(msg.text) - int(balance_binance[0])} USDT and create a new request!</em>"
                        await msg.answer(text)
                else:
                    deposit = await balance.get_balance(msg.from_id)
                    if int(deposit[1]) + int(msg.text) >= 15000:
                        if int(balance_binance[0]) >= int(msg.text):
                            await balance.insert_deposit(msg.from_id, int(msg.text))
                            await users.set_status("15000", msg.from_id)
                            await balance.insert_balance_history(msg.from_id, int(msg.text), "Личный аккаунт")
                            text = f"Ваш Баланс Binance: {balance_binance[0]}\n\n" \
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
                                text = f"Your Binance Balance: {balance_binance[0]}\n\n" \
                                       "Deposit successfully completed.\n\n<em>We will notify you when trading starts" \
                                       " and will stay in touch with you. You can make withdrawals at any time by " \
                                       "submitting a prior request. This is necessary for us to close open orders and" \
                                       " ensure that you do not lose your profitability.\n\nTo make a withdrawal " \
                                       "request, please use the chat bot in the 'Withdraw' section. We will provide " \
                                       "you with a recommendation on the " \
                                       "optimal timing for withdrawal to maximize your returns. " \
                                       "The processing time for withdrawal " \
                                       "requests is up to 24 hours.\n\nWhen making withdrawals without a request, the" \
                                       " company reserves the right to disable the account from the referral " \
                                       "and incentive program, with a subsequent ban for six months!</em>"
                            await msg.answer(text)
                        else:
                            x = int(msg.text)
                            if 15000 > int(msg.text):
                                x = 15000
                            text = f"<b>Сумма на вашем аккаунте Binance не может быть меньше, чем сумма пополнения!" \
                                   f"</b>\n\n<em>Для продолжения пополните аккаунт на сумму " \
                                   f"{x - int(balance_binance[0])} USDT и создайте новую заявку!</em>"
                            if language[4] == "EN":
                                text = f"<b>The amount in your Binance account cannot be less than the top-up amount!" \
                                       f"</b>\n\n<em>To proceed, please top up your account with an amount of " \
                                       f"{x - int(balance_binance[0])} USDT and create a new request!</em>"
                            await msg.answer(text)

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
        else:
            text = f"<b>Произошла ошибка, обратитесь в поддержку! \n\n" \
                   f"(API Key или Api Secret некорректны)</b>"
            if language[4] == "EN":
                text = f"<b>An error occurred. Please contact support! (API Key or API Secret is incorrect)</b>"
            await msg.answer(text, reply_markup=await inline.main_menu(language[4], msg.from_user.id))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(refill_handler, text='refill', state="*")
    dp.register_callback_query_handler(handle_deposit_funds, text='deposit_funds')
    dp.register_callback_query_handler(handle_review_terms, text='review_terms')
    dp.register_callback_query_handler(handle_distribution, text='distribution')
    dp.register_callback_query_handler(handle_500_15000, lambda c: c.data in ['active_500', 'active_15000'])
    dp.register_callback_query_handler(handle_emailing_documents, text='emailing_documents')
    dp.register_callback_query_handler(handle_emailing_alias, state=BinanceAPI.alias)
    dp.register_callback_query_handler(biguser_registration, text="15000")
    dp.register_callback_query_handler(biguser_registration_step_1, state=BigUser.binance)
    dp.register_callback_query_handler(biguser_registration_step_2, state=BigUser.kyc)
    # dp.register_message_handler(biguser_registration_step3, content_types=['text', 'video', 'photo', 'document'],
    #                             state=BigUser.contract)
    dp.register_message_handler(binanceapi_step1_msg, state=BigUser.finish)
    # dp.register_message_handler(binanceapi_step2, state=BinanceAPI.alias)
    # dp.register_message_handler(binance_step3, state=BinanceAPI.api_key)
    # dp.register_message_handler(binance_step4, state=BinanceAPI.api_secret)
    dp.register_message_handler(count_refill, state=Refill.count)
    dp.register_callback_query_handler(new_docs_2, state=NewDoc.docs)
    dp.register_callback_query_handler(new_docs_3, state=NewDoc.docs_2)
