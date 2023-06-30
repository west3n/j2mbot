import asyncio
import random
import re
import string

import decouple
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from keyboards import inline
from database import users, balance, referral, nft, thedex_db
from aiogram.dispatcher.filters.state import StatesGroup, State
import shutup
from binance import thedex, microservice
from handlers.google import send_email_message

shutup.please()


class Registration(StatesGroup):
    language = State()
    accept = State()
    finish = State()
    email = State()
    ver_code = State()
    one_more = State()


class SmartContract(StatesGroup):
    new_referral = State()
    mint_nft = State()
    start_minting = State()


class Email(StatesGroup):
    email = State()
    ver_code = State()
    one_more = State()


async def file_id(msg: types.Message):
    if str(msg.from_id) in ['254465569', '15362825']:
        if msg.document:
            await msg.reply(msg.document.file_id)
        if msg.photo:
            await msg.reply(msg.photo[-1].file_id)
        if msg.animation:
            await msg.reply(msg.animation.file_id)
        if msg.video:
            await msg.reply(msg.video.file_id)


async def bot_start(msg: types.Message, state: FSMContext):
    if msg.chat.type == "private":
        email_ = await users.check_email(msg.from_id)
        try:
            email_ = email_[0]
        except TypeError:
            email_ = None
        nft_ = await nft.check_nft_status(msg.from_id)
        await state.finish()
        user_status = await users.user_data(msg.from_user.id)
        wallet = await balance.get_balance_status(msg.from_id)
        if user_status and wallet and nft_ and email_:
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
                reply_markup=await inline.main_menu(language[4], msg.from_id))
        elif user_status and nft_ and email_:
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
                    video = decouple.config("NFT_ANIMATION")
                    invitor = await referral.get_id_from_line_1_id(msg.from_user.id)
                    try:
                        invitor = invitor[0]
                    except TypeError:
                        invitor = 32591016
                    try:
                        resp, private_key, address = await microservice.microservice_(msg.from_user.id, invitor)
                        dao = await nft.update_nft(msg.from_user.id, address, private_key, "Successful")
                    except TypeError:
                        resp = None
                        address = None
                        private_key = None
                        dao = None
                    if resp:
                        email_ad = await users.check_email(msg.from_user.id)
                        invite_link = await msg.bot.create_chat_invite_link(chat_id=decouple.config('J2M_CHAT'))
                        text = f"Транзакция прошла успешно!" \
                               f"\n\nПоздравляем с приобретением NFT участия в нашем ДАО!" \
                               f"\nВаш индивидуальный номер участника DAO: {dao[0]}" \
                               f"\nТеперь вам доступен полный функционал бота." \
                               f"\n\nВы стали частью нашей активной и развивающейся организации. Ваш NFT будет служить " \
                               f"подтверждением вашего статуса и прав в рамках нашего ДАО." \
                               f"\n\nВместе мы выбираем устойчивые решения по увеличению своих цифровых активов, " \
                               f"создаем будущее и осознанно используем современные технологии. Удачи в Вашем дальнейшем " \
                               f"развитии совместно с DAO J2M!" \
                               f"\n\nNFT хранится на защищенном кошельке созданном специально для вас. " \
                               f"Данные по NFT отправляются автоматически вам на почту." \
                               f"\n\nВ дальнейшем Вы сможете перевести её на любой другой ваш кошелек. " \
                               f"\n\nNFT хранится на сервере DAO J2M, " \
                               f"если вы потеряли или забыли номер кошелька или ключ обратитесь в службу поддержки." \
                               f"\n\nСсылка-приглашение в закрытый DAO J2M чат: {invite_link.invite_link}"

                        email_text = f"Транзакция прошла успешно!" \
                                     f"\n\nПоздравляем с приобретением NFT участия в нашем ДАО!" \
                                     f"\nВаш индивидуальный номер участника DAO: {dao[0]}" \
                                     f"\nТеперь вам доступен полный функционал бота." \
                                     f"\n\nВы стали частью нашей активной и развивающейся организации. Ваш NFT будет служить " \
                                     f"подтверждением вашего статуса и прав в рамках нашего ДАО." \
                                     f"\n\nВместе мы выбираем устойчивые решения по увеличению своих цифровых активов, " \
                                     f"создаем будущее и осознанно используем современные технологии. Удачи в Вашем дальнейшем " \
                                     f"развитии совместно с DAO J2M!" \
                                     f"\n\nNFT хранится на защищенном кошельке созданном специально для вас. " \
                                     f"\n\nАдрес кошелька с NFT: {address}\n" \
                                     f"Приватный ключ: {private_key}\n\n" \
                                     f"\n\nВ дальнейшем Вы сможете перевести её на любой другой ваш кошелек. " \
                                     f"\n\nNFT хранится на сервере DAO J2M, " \
                                     f"если вы потеряли или забыли номер кошелька или ключ обратитесь в службу поддержки."
                        if language[4] == "EN":
                            video = decouple.config("NFT_ANIMATION_EN")
                            text = f"Transaction completed successfully!" \
                                   f"\n\nCongratulations on acquiring the participation NFT in our DAO!" \
                                   f"\nYour unique DAO participant number is {dao[0]}.\nYou now have full access to the " \
                                   f"bot functionality.\n\nYou have become part of our active and growing organization. " \
                                   f"Your NFT will serve as confirmation of your status and rights within our DAO." \
                                   f"\n\nTogether, we choose sustainable solutions to increase our digital assets, " \
                                   f"create the future, and consciously utilize modern technologies. " \
                                   f"Best of luck in your further development alongside DAO J2M!" \
                                   f"\n\nYour NFT is stored in a secure wallet created specifically for you. " \
                                   f"\n\nIn the future, you will be able to transfer it to any other wallet of yours. " \
                                   f"You can find more information about this in the 'Information' section."
                            email_text = f"The transaction was successful!"
                            f"\n\nCongratulations on acquiring an NFT participation in our DAO!"
                            f"\nYour unique DAO participant number: {dao[0]}"
                            f"\nNow you have access to the full functionality of the bot."
                            f"\n\nYou have become part of our active and growing organization. Your NFT will serve as"
                            f"confirmation of your status and rights within our DAO."
                            f"\n\nTogether, we make sustainable decisions to increase our digital assets, create the future,"
                            f"and consciously use modern technologies. Good luck in your future development with DAO J2M!"
                            f"\n\nThe NFT is stored in a secure wallet created specifically for you."
                            f"\n\nWallet address with NFT: {address}\n"
                            f"Private key: {private_key}\n\n"
                            f"\n\nIn the future, you will be able to transfer it to any other wallet you own."
                            f"\n\nThe NFT is stored on the DAO J2M server. If you have lost or forgotten the wallet address"
                            f"or key, please contact customer support."
                        await send_email_message(to=email_ad[0],
                                                 subject="DAO J2M Smart Contract",
                                                 message_text=email_text)
                        await msg.answer_video(video=video,
                                               caption=text, reply_markup=inline.main_menu_short(language[4]))
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
        elif not email_:
            await email(msg)
        elif not nft_:
            await nft_start(msg)
        if msg.get_args():
            if int(msg.get_args()) == msg.from_id:
                pass
            else:
                # Добавление нового реферала
                try:
                    await referral.add_first_line(int(msg.get_args()), msg.from_id)
                    text = f"Пользователь {msg.from_id} - {msg.from_user.full_name if msg.from_user.username is None else '@' + msg.from_user.username} " \
                           f"зарегистрировался по вашей партнерской программе!"
                    await msg.bot.send_message(chat_id=int(msg.get_args()),
                                               text=text)
                except:
                    pass
    else:
        if str(msg.from_id) in ['254465569', '15362825']:
            await msg.answer("Привет, создатель! 💋")
        else:
            await msg.answer("Ой, я не умею работать в группе 😰"
                             f"\n{msg.from_user.full_name}, ты можешь поблагодарить @Caramba и @miroshnikov за создание "
                             f"меня!")


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
            reply_markup=await inline.main_menu(language[4], call.from_user.id))
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
                video = decouple.config("NFT_ANIMATION")
                invitor = await referral.get_id_from_line_1_id(call.from_user.id)
                try:
                    invitor = invitor[0]
                except TypeError:
                    invitor = 32591016
                try:
                    resp, private_key, address = await microservice.microservice_(call.from_user.id, invitor)
                    dao = await nft.update_nft(call.from_user.id, address, private_key, "Successful")
                except TypeError:
                    resp = None
                    address = None
                    private_key = None
                    dao = None
                if resp:
                    email_ad = await users.check_email(call.from_user.id)
                    invite_link = await call.bot.create_chat_invite_link(chat_id=decouple.config('J2M_CHAT'))
                    text = f"Транзакция прошла успешно!" \
                           f"\n\nПоздравляем с приобретением NFT участия в нашем ДАО!" \
                           f"\nВаш индивидуальный номер участника DAO: {dao[0]}" \
                           f"\nТеперь вам доступен полный функционал бота." \
                           f"\n\nВы стали частью нашей активной и развивающейся организации. Ваш NFT будет служить " \
                           f"подтверждением вашего статуса и прав в рамках нашего ДАО." \
                           f"\n\nВместе мы выбираем устойчивые решения по увеличению своих цифровых активов, " \
                           f"создаем будущее и осознанно используем современные технологии. Удачи в Вашем дальнейшем " \
                           f"развитии совместно с DAO J2M!" \
                           f"\n\nNFT хранится на защищенном кошельке созданном специально для вас. " \
                           f"Данные по NFT отправляются автоматически вам на почту." \
                           f"\n\nСсылка-приглашение в закрытый DAO J2M чат: {invite_link.invite_link}"
                    email_text = f"Транзакция прошла успешно!" \
                           f"\n\nПоздравляем с приобретением NFT участия в нашем ДАО!" \
                           f"\nВаш индивидуальный номер участника DAO: {dao[0]}" \
                           f"\nТеперь вам доступен полный функционал бота." \
                           f"\n\nВы стали частью нашей активной и развивающейся организации. Ваш NFT будет служить " \
                           f"подтверждением вашего статуса и прав в рамках нашего ДАО." \
                           f"\n\nВместе мы выбираем устойчивые решения по увеличению своих цифровых активов, " \
                           f"создаем будущее и осознанно используем современные технологии. Удачи в Вашем дальнейшем " \
                           f"развитии совместно с DAO J2M!" \
                           f"\n\nNFT хранится на защищенном кошельке созданном специально для вас. " \
                           f"\n\nАдрес кошелька с NFT: {address}\n" \
                           f"Приватный ключ: {private_key}\n\n"\
                           f"\n\nВ дальнейшем Вы сможете перевести её на любой другой ваш кошелек. " \
                           f"\n\nNFT хранится на сервере DAO J2M, " \
                           f"если вы потеряли или забыли номер кошелька или ключ обратитесь в службу поддержки."
                    if language[4] == "EN":
                        video = decouple.config("NFT_ANIMATION_EN")
                        text = f"Transaction completed successfully!" \
                               f"\n\nCongratulations on acquiring the participation NFT in our DAO!" \
                               f"\nYour unique DAO participant number is {dao[0]}.\nYou now have full access to the " \
                               f"bot functionality.\n\nYou have become part of our active and growing organization. " \
                               f"Your NFT will serve as confirmation of your status and rights within our DAO." \
                               f"\n\nTogether, we choose sustainable solutions to increase our digital assets, " \
                               f"create the future, and consciously utilize modern technologies. " \
                               f"Best of luck in your further development alongside DAO J2M!" \
                               f"\n\nYour NFT is stored in a secure wallet created specifically for you. " \
                               f"\n\nIn the future, you will be able to transfer it to any other wallet of yours. " \
                               f"You can find more information about this in the 'Information' section." \
                               f"\n\nInvitation link to the closed <a href='{invite_link.invite_link}'>J2M DAO chat</a>"

                        email_text = f"The transaction was successful!"
                        f"\n\nCongratulations on acquiring an NFT participation in our DAO!"
                        f"\nYour unique DAO participant number: {dao[0]}"
                        f"\nNow you have access to the full functionality of the bot."
                        f"\n\nYou have become part of our active and growing organization. Your NFT will serve as"
                        f"confirmation of your status and rights within our DAO."
                        f"\n\nTogether, we make sustainable decisions to increase our digital assets, create the future,"
                        f"and consciously use modern technologies. Good luck in your future development with DAO J2M!"
                        f"\n\nThe NFT is stored in a secure wallet created specifically for you."
                        f"\n\nWallet address with NFT: {address}\n"
                        f"Private key: {private_key}\n\n"
                        f"\n\nIn the future, you will be able to transfer it to any other wallet you own."
                        f"\n\nThe NFT is stored on the DAO J2M server. If you have lost or forgotten the wallet address"
                        f"or key, please contact customer support."
                    await send_email_message(to=email_ad[0],
                                             subject="DAO J2M Smart Contract",
                                             message_text=email_text)
                    await call.message.answer_video(video=video,
                                                    caption=text,
                                                    reply_markup=inline.main_menu_short(language[4]))
                    await call.bot.send_message(chat_id=decouple.config('GROUP_ID'),
                                                text=f"Пользователь {call.from_user.id} - {call.from_user.username} получил NFT (РЕКЛАМА)"
                                                     f"\n\nПодробнее по ссылке: http://89.223.121.160:8000/admin/app/nft/")
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
    if msg.chat.type == "private":
        await state.finish()
        await msg.answer("Для комфортной работы с ботом, выберите язык:"
                         "\nTo ensure smooth interaction with the bot, please select a language:",
                         reply_markup=inline.language())
        await Registration.language.set()
    else:
        mess = await msg.answer("Не-а, больше не получится!")
        await asyncio.sleep(2)
        await msg.bot.delete_message(chat_id=decouple.config('GROUP_ID'), message_id=mess.message_id)


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
        await call.message.answer_photo(photo=photo, caption=text,
                                        reply_markup=await inline.main_menu(language[4], call.from_user.id))


async def nft_refill(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    count = await nft.check_nft_count()
    summ = 48
    if count <= 555:
        summ = 8.5
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


async def cancel_payment(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    language = await users.user_data(call.from_user.id)
    try:
        await call.message.delete()
    except:
        pass
    transaction = await thedex_db.get_transaction(call.from_user.id)
    try:
        transaction = transaction[0]
        await thedex_db.delete_transaction(transaction[0])
    except:
        pass
    photo = decouple.config('BANNER_MAIN')
    text = "Транзакция успешно отменена!"
    if language[4] == "EN":
        text = "Transaction successfully canceled!"
        photo = decouple.config('BANNER_MAIN_EN')
    await call.message.answer_photo(photo=photo, caption=text, reply_markup=await inline.main_menu(language[4], call.from_user.id))


async def email(msg: types.Message):
    language = await users.user_data(msg.from_user.id)
    try:
        await msg.delete()
    except:
        pass
    text = f"Для продолжения укажите ваш действующий личный e-mail.\n\n" \
           f"<em>На почту придет сообщение с верификационным кодом, так же при потере доступа к боту вы сможете " \
           f"восстановить свой аккаунт через почту!</em>"
    if language[4] == "EN":
        text = f"To proceed, please provide your current personal email.\n\n"
        f"<em>You will receive a message with a verification code to your email. In case you lose access to the bot, "
        f"you will be able to recover your account through email!</em>"
    await msg.answer(text)
    await Email.email.set()


def generate_random_code():
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(6))
    return code


async def email_message(msg: types.Message, state: FSMContext):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    language = await users.user_data(msg.from_user.id)
    if re.match(pattern, msg.text):
        code = generate_random_code()
        async with state.proxy() as data:
            await state.update_data({"email": msg.text, "code": code})
        text = f"На указанную почту {msg.text} было отправлено письмо.\n\n" \
               f"Пожалуйста, введите уникальный код из письма:"
        email_text = f"Вас приветствует команда DAO J2M!\n\n" \
                         f"Для завершения верификации, отправьте боту этот код: {code}" \
                         f"\n\nЕсли у вас возникли сложности, или вам нужна помощь, вы можете связаться с нами по " \
                                   f"этой электронной почте ответным письмом, или напишите нам в телеграм: " \
                                   f"https://t.me/J2M_Support "
        if language[4] == "EN":
            text = f"An email has been sent to the provided email address {msg.text}.\n\n"
            f"Please enter the unique code from the email:"
            email_text = f"Greetings from the DAO J2M team!\n\n"
            f"To complete the verification, please send this code to the bot: {code}"
            f"\n\nIf you encounter any difficulties or need assistance, you can contact us via "
            f"this email by replying to this message, or reach out to us on Telegram: "
            f"https://t.me/J2M_Support"

        await send_email_message(to=msg.text,
                                 subject="DAO J2M verification",
                                 message_text=email_text)
        await msg.answer(text)
        await Email.next()
    else:
        text = "Указанная почта не является email. Пожалуйста напишите почту еще раз:"
        if language[4] == "EN":
            text = "The provided email address is not valid. Please enter your email again:"
        await msg.answer(text)


async def ver_code(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if msg.text == data.get("code"):
            await msg.answer("Верификация успешно пройдена.")
            await users.insert_email(msg.from_id, data.get('email'))
            await bot_start(msg, state)
        else:
            text = "Введен некорректный код верификации!"
            language = data.get('language')
            if language == "EN":
                text = "Invalid verification code entered!"
            await msg.answer(text, reply_markup=inline.email_verif(language))
            await Email.next()


async def one_more(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    try:
        await call.message.delete()
    except:
        pass
    if call.data == "new_code":
        async with state.proxy() as data:
            code = generate_random_code()
            await state.update_data({"code": code})
            email_text = f"Вас приветствует команда DAO J2M!\n\n" \
                         f"Для завершения верификации, отправьте боту этот код: {code}" \
                         f"\n\nЕсли у вас возникли сложности, или вам нужна помощь, вы можете связаться с нами по " \
                         f"этой электронной почте ответным письмом, или напишите нам в телеграм: " \
                         f"https://t.me/J2M_Support "
            text = f"На указанную почту было отправлено письмо. Оно может находится в спаме, пожалуйста проверьте.\n\n" \
                   f"Пожалуйста, введите уникальный код из письма:"
            if language[4] == "EN":
                text = f"An email has been sent to the provided email address.\n\n"
                f"Please enter the unique code from the email:"
                email_text = f"Greetings from the DAO J2M team!\n\n"
                f"To complete the verification, please send this code to the bot: {code}"
                f"\n\nIf you encounter any difficulties or need assistance, you can contact us via "
                f"this email by replying to this message, or reach out to us on Telegram: "
                f"https://t.me/J2M_Support"
            await send_email_message(to=data.get('email'),
                                     subject="DAO J2M verification",
                                     message_text=email_text)
            await call.message.answer(text)
            await state.set_state(Email.ver_code.state)
    if call.data == "change_email":
        text = f"Для продолжения укажите ваш действующий личный e-mail.\n\n" \
               f"<em>На почту придет сообщение с верификационным кодом, так же при потере доступа к боту вы сможете " \
               f"восстановить свой аккаунт через почту!</em>"
        if language[4] == "EN":
            text = f"To proceed, please provide your current personal email.\n\n"
            f"<em>You will receive a message with a verification code to your email. In case you lose access to the bot, "
            f"you will be able to recover your account through email!</em>"
        await call.message.answer(text)
        await state.set_state(Email.email.state)


def register(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_payment, text="cancel_payment", state="*")
    dp.register_message_handler(file_id, content_types=['photo', 'document', 'animation', 'video'], state="*")
    dp.register_message_handler(bot_start, commands='start', state='*')
    dp.register_message_handler(select_language, commands='language', state='*')
    dp.register_callback_query_handler(bot_start_call, text='main_menu')
    dp.register_callback_query_handler(all_support, lambda c: c.data in ['support_nft', 'support_short', 'support'],
                                       state="*")
    dp.register_callback_query_handler(back_button, lambda c: c.data in ['nft_kb', 'short_kb', 'menu_kb'])
    dp.register_callback_query_handler(nft_refill, text="get_nft")
    dp.register_message_handler(email_message, state=Email.email)
    dp.register_message_handler(ver_code, state=Email.ver_code)
    dp.register_callback_query_handler(one_more, state=Email.one_more)
