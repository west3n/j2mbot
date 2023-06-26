import decouple
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from keyboards import inline
from database import users, balance, referral, nft
from aiogram.dispatcher.filters.state import StatesGroup, State
import shutup
from binance import thedex, microservice

shutup.please()


class Registration(StatesGroup):
    language = State()
    accept = State()
    finish = State()


class SmartContract(StatesGroup):
    new_referral = State()
    mint_nft = State()
    start_minting = State()


async def file_id(msg: types.Message):
    if str(msg.from_id) in ['254465569', '15362825']:
        if msg.document:
            await msg.reply(msg.document.file_id)
        if msg.photo:
            await msg.reply(msg.photo[-1].file_id)
        if msg.animation:
            await msg.reply(msg.animation.file_id)


async def bot_start(msg: types.Message, state: FSMContext):
    nft_ = await nft.check_nft_status(msg.from_id)
    await state.finish()
    user_status = await users.user_data(msg.from_user.id)
    wallet = await balance.get_balance_status(msg.from_id)
    if user_status and wallet and nft_:
        name = msg.from_user.first_name
        language = await users.user_data(msg.from_user.id)
        text = f"{name}, выберите интересующий Вас раздел, нажав одну из кнопок ниже"
        photo = decouple.config("BANNER_MAIN")
        if language[4] == 'EN':
            text = f"{name}, please select the section of interest by clicking one of the buttons below:"
            photo = decouple.config("BANNER_MAIN_EN")
        await msg.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=inline.main_menu(language[4]))
    elif user_status and nft_:
        if nft_[1]:
            name = msg.from_user.first_name
            language = await users.user_data(msg.from_user.id)
            text = f"{name}, выберите интересующий Вас раздел, нажав одну из кнопок ниже"
            photo = decouple.config("BANNER_MAIN")
            if language[4] == 'EN':
                text = f"{name}, please select the section of interest by clicking one of the buttons below:"
                photo = decouple.config("BANNER_MAIN_EN")
            await msg.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=inline.main_menu_short(language[4]))
        else:
            language = await users.user_data(msg.from_user.id)
            invoiceId = await nft.check_nft_status(msg.from_user.id)
            status = await thedex.invoice_one(invoiceId[5])
            if status == "Waiting":
                text = "Нужно еще немного времени на проверку, пожалуйста, повторите позже"
                if language[4] == "EN":
                    text = "Further time is needed for verification. Please try again later."
                await msg.answer(text, reply_markup=inline.check_nft_status(language[4]))

            elif status == "Unpaid":
                text = "Вы не успели оплатить. Процедуру необходимо провести заново\n\n"
                if language[4] == "EN":
                    text = "You missed the payment deadline. The procedure needs to be repeated.\n\n"
                await msg.answer(text)
                await nft.delete_error(msg.from_user.id)

            elif status == "Successful":
                invitor = await referral.get_id_from_line_1_id(msg.from_user.id)
                try:
                    invitor = invitor[0]
                except TypeError:
                    invitor = 1
                try:
                    resp, private_key, address = await microservice.microservice_(msg.from_user.id, invitor)
                    await nft.update_nft(msg.from_user.id, address, private_key, "Succsesful")
                except TypeError:
                    resp = None
                    address = None
                    private_key = None
                if resp:
                    text = f"Оплата прошла успешно.\n\n" \
                           f"Адрес кошелька с NFT: {address}\n" \
                           f"Приватный ключ: {private_key}\n\n" \
                           f"Рекомендуем удалить это сообщение после сохранения в заметки."

                    if language[4] == "EN":
                        text = f"The payment was successful.\n\n"
                        f"Wallet address with NFT: {address}\n"
                        f"Private key: {private_key}\n\n"
                        f"We recommend deleting this message after saving the information in your notes."

                    await msg.answer(text, reply_markup=inline.main_menu_short(language[4]))
                else:
                    text = "Произошла ошибка, обратитесь в поддержку"
                    if language[4] == "EN":
                        text = "An error occurred. Please contact support."
                await msg.answer(text, reply_markup=inline.main_menu_short(language[4]))
            elif status == "Rejected":
                text = "Произошла ошибка. Деньги вернуться к вам на счет."
                if language[4] == "EN":
                    text = "An error occurred. The money will be refunded to your account."
                await msg.answer(text)
                await nft.delete_error(msg.from_user.id)
    elif not user_status:
        await msg.answer("Для комфортной работы с ботом, выберите язык:"
                         "\nTo ensure smooth interaction with the bot, please select a language:",
                         reply_markup=inline.language())
        await Registration.language.set()
    elif not nft_:
        await nft_start(msg)
    if msg.get_args():
        if int(msg.get_args()) == msg.from_id:
            pass
        else:
            await referral.add_first_line(int(msg.get_args()), msg.from_id)


async def nft_start(msg: types.Message):
    language = await users.user_data(msg.from_user.id)
    try:
        ref_tg = await referral.get_id_from_line_1_id(msg.from_user.id)
        ref_full_name = await users.get_tg_full_name(ref_tg[0])
    except TypeError:
        ref_tg = None
        ref_full_name = None
    if ref_tg:
        print(language[4])
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
        if language[4] == "EN":
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
        await msg.answer(text, reply_markup=inline.yesno_refill(language[4]))
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
        if language[4] == "EN":
            text = f"We strive to create a community based on interaction and collaboration among our members.\n\n"
            f"According to our rules, which you have accepted, before you can take advantage of all the opportunities "
            f"provided by our DAO, we kindly ask you to confirm that the information about the possibility of joining "
            f"our community was found independently by you. This ensures an additional level of trust and helps us "
            f"confirm your legitimacy in our DAO.\n\n"
            f"Note: After this confirmation, it will be impossible to change this information, as in the next "
            f"registration stage, these data will be entered into the DAO smart contract."
        await msg.answer(text, reply_markup=inline.yesno_refill(language[4]))
    await SmartContract.mint_nft.set()


async def nft_start_call(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    try:
        ref_tg = await referral.get_id_from_line_1_id(call.from_user.id)
        ref_full_name = await users.get_tg_full_name(ref_tg[0])
    except TypeError:
        ref_tg = None
        ref_full_name = None
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
        if language[4] == "EN":
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
        await call.message.answer(text, reply_markup=inline.yesno_refill(language[4]))
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
        await call.message.answer(text, reply_markup=inline.yesno_refill(language[4]))
    await SmartContract.mint_nft.set()


async def bot_start_call(call: types.CallbackQuery):
    try:
        await call.message.delete()
    except:
        pass
    nft_ = await nft.check_nft_status(call.from_user.id)
    user_status = await users.user_data(call.from_user.id)
    wallet = await balance.get_balance_status(call.from_user.id)
    if user_status and wallet and nft_:
        name = call.from_user.first_name
        language = await users.user_data(call.from_user.id)
        text = f"{name}, выберите интересующий Вас раздел, нажав одну из кнопок ниже"
        photo = decouple.config("BANNER_MAIN")
        if language[4] == 'EN':
            text = f"{name}, please select the section of interest by clicking one of the buttons below:"
            photo = decouple.config("BANNER_MAIN_EN")
        await call.message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=inline.main_menu(language[4]))
    elif user_status and nft_:
        if nft_[1]:
            name = call.from_user.first_name
            language = await users.user_data(call.from_user.id)
            text = f"{name}, выберите интересующий Вас раздел, нажав одну из кнопок ниже"
            photo = decouple.config("BANNER_MAIN")
            if language[4] == 'EN':
                text = f"{name}, please select the section of interest by clicking one of the buttons below:"
                photo = decouple.config("BANNER_MAIN_EN")
            await call.message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=inline.main_menu_short(language[4]))
        else:
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
                invitor = await referral.get_id_from_line_1_id(call.from_user.id)
                try:
                    invitor = invitor[0]
                except TypeError:
                    invitor = 1
                try:
                    resp, private_key, address = await microservice.microservice_(call.from_user.id, invitor)
                    await nft.update_nft(call.from_user.id, address, private_key, "Succsesful")
                except TypeError:
                    resp = None
                    address = None
                    private_key = None
                if resp:
                    text = f"Оплата прошла успешно.\n\n" \
                           f"Адрес кошелька с NFT: {address}\n" \
                           f"Приватный ключ: {private_key}\n\n" \
                           f"Рекомендуем удалить это сообщение после сохранения в заметки."

                    if language[4] == "EN":
                        text = f"The payment was successful.\n\n"
                        f"Wallet address with NFT: {address}\n"
                        f"Private key: {private_key}\n\n"
                        f"We recommend deleting this message after saving the information in your notes."

                    await call.message.answer(text, reply_markup=inline.main_menu_short(language[4]))
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
    elif not user_status:
        await call.message.answer("Для комфортной работы с ботом, выберите язык:"
                                  "\nTo ensure smooth interaction with the bot, please select a language:",
                                  reply_markup=inline.language())
        await Registration.language.set()
    elif not nft_:
        await nft_start_call(call)


async def select_language(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Для комфортной работы с ботом, выберите язык:"
                     "\nTo ensure smooth interaction with the bot, please select a language:",
                     reply_markup=inline.language())
    await Registration.language.set()


async def all_support(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    photo = decouple.config('BANNER_SUPPORT')
    language = await users.user_data(call.from_user.id)
    text = "Добро пожаловать в службу поддержки!\n\nВ зависимости от вашего вопроса, вы можете обратиться к поддержке " \
           "DAO J2M или к поддержке наших партнеров по предоставлению IT продуктов.\n\nПоддержка DAO J2M\nМы " \
           "предоставляем поддержку не только в использовании нашего бота, но и во всех вопросах, связанных с " \
           "участием в DAO J2M. Наша команда готова помочь вам с любыми техническими вопросами и решить возникшие " \
           "проблемы.\n\nПоддержка компании SONERA - партнеров DAO J2M\nОни стремятся сделать ваш опыт использования " \
           "их продуктов максимально удобным и эффективным. Они предлагают надежные и интуитивно понятные процедуры, " \
           "которые помогут вам получить доступ к интеграции и всем возможностям предлагаемых продуктов.\n\nМы " \
           "гарантируем, что вы получите необходимую информацию и помощь на всех этапах взаимодействия с " \
           "нами.\n\nОбращения обрабатываются в порядке живой очереди, поэтому не рекомендуем писать их повторно. " \
           "Максимальное время ответа 6 часов. Мы будем сокращать ваше время ожидания и стараться ответить вам как " \
           "можно быстрее. "
    if language[4] == "EN":
        photo = decouple.config('BANNER_SUPPORT_EN')
        text = "Welcome to the support service!\n\nDepending on your question, you can contact DAO J2M support or our " \
               "partners' support for IT products.\n\nDAO J2M Support\nWe provide support not only in using our bot " \
               "but also in all matters related to participating in DAO J2M. Our team is ready to assist you with any " \
               "technical questions and resolve any issues that may arise.\n\nSONERA Company - DAO J2M Partners " \
               "Support\nThey strive to make your experience with their products as convenient and efficient as " \
               "possible. They offer reliable and intuitively understandable procedures that will help you access " \
               "integration and all the features offered by the products.\n\nWe guarantee that you will receive the " \
               "necessary information and assistance at every stage of interaction with us.\n\nInquiries are " \
               "processed in a live queue, so we do not recommend submitting them repeatedly. The maximum response " \
               "time is 6 hours. We will reduce your waiting time and strive to answer you as quickly as possible. "
    if call.data == "support_nft":
        await call.message.answer_photo(photo=photo, caption=text, reply_markup=inline.support_menu("nft_kb"))
    elif call.data == "support_short":
        await call.message.answer_photo(photo=photo, caption=text, reply_markup=inline.support_menu("short_kb"))
    elif call.data == "support":
        await call.message.answer_photo(photo=photo, caption=text, reply_markup=inline.support_menu("menu_kb"))


async def back_button(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    if call.data == "nft_kb":
        text = "Для продолжения, вам необходимо приобрести NFT."
        if language[4] == "EN":
            text = "To proceed, you need to purchase an NFT."
        await call.message.answer(text, reply_markup=inline.get_nft(language[4]))
    elif call.data == "short_kb":
        text = "Главное меню"
        photo = decouple.config('BANNER_MAIN')
        if language[4] == "EN":
            text = "Main menu"
            photo = decouple.config('BANNER_MAIN_EN')
        await call.message.answer_photo(photo=photo, caption=text, reply_markup=inline.main_menu_short(language[4]))
    elif call.data == "menu_kb":
        text = "Главное меню"
        photo = decouple.config('BANNER_MAIN')
        if language[4] == "EN":
            text = "Main menu"
            photo = decouple.config('BANNER_MAIN_EN')
        await call.message.answer_photo(photo=photo, caption=text, reply_markup=inline.main_menu(language[4]))


async def nft_refill(call: types.CallbackQuery):
    await call.message.delete()
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
    await call.message.answer(text, parse_mode=types.ParseMode.MARKDOWN_V2,
                              reply_markup=inline.check_nft_status(language[4]))


def register(dp: Dispatcher):
    dp.register_message_handler(file_id, content_types=['photo', 'document', 'animation'], state="*")
    dp.register_message_handler(bot_start, commands='start', state='*')
    dp.register_message_handler(select_language, commands='language', state='*')
    dp.register_callback_query_handler(bot_start_call, text='main_menu')
    dp.register_callback_query_handler(all_support, lambda c: c.data in ['support_nft', 'support_short', 'support'],
                                       state="*")
    dp.register_callback_query_handler(back_button, lambda c: c.data in ['nft_kb', 'short_kb', 'menu_kb'])
    dp.register_callback_query_handler(nft_refill, text="get_nft")
