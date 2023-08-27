import asyncio
import random
import re
import string
import decouple
import shutup

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound
from keyboards import inline
from database import users, balance, referral, nft, thedex_db
from aiogram.dispatcher.filters.state import StatesGroup, State
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
            language = await users.user_data(msg.from_user.id)
            text = "Загружаю главное меню..."
            if language[4] == 'EN':
                text = "Loading main menu..."
            start_message = await msg.answer(text)
            name = msg.from_user.first_name
            language = await users.user_data(msg.from_user.id)
            text = f"{name}, выберите интересующий Вас раздел, нажав одну из кнопок ниже"
            photo = decouple.config("BANNER_MAIN")
            if language[4] == 'EN':
                text = f"{name}, please select the section of interest by clicking one of the buttons below:"
                photo = decouple.config("BANNER_MAIN_EN")
            try:
                await msg.bot.delete_message(msg.chat.id, start_message.message_id)
            except MessageToDeleteNotFound:
                pass
            await msg.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=await inline.main_menu(language[4], msg.from_id))
        elif user_status and nft_ and email_:
            if nft_[1]:
                language = await users.user_data(msg.from_user.id)
                text = "Загружаю главное меню..."
                if language[4] == 'EN':
                    text = "Loading main menu..."
                start_message = await msg.answer(text)
                name = msg.from_user.first_name
                language = await users.user_data(msg.from_user.id)
                text = f"{name}, выберите интересующий Вас раздел, нажав одну из кнопок ниже"
                photo = decouple.config("BANNER_MAIN")
                if language[4] == 'EN':
                    text = f"{name}, please select the section of interest by clicking one of the buttons below:"
                    photo = decouple.config("BANNER_MAIN_EN")
                try:
                    await msg.bot.delete_message(msg.chat.id, start_message.message_id)
                except MessageToDeleteNotFound:
                    pass
                await msg.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=inline.main_menu_short(language[4]))
            else:
                language = await users.user_data(msg.from_user.id)
                text = "Загружаю главное меню..."
                if language[4] == 'EN':
                    text = "Loading main menu..."
                start_message = await msg.answer(text)
                invoiceId = await nft.check_nft_status(msg.from_user.id)
                status, title = await thedex.invoice_one(invoiceId[5])
                if status == "Waiting":
                    text = await users.get_text('Статус Waiting у NFT', language[4])
                    try:
                        await msg.bot.delete_message(msg.chat.id, start_message.message_id)
                    except MessageToDeleteNotFound:
                        pass
                    await msg.answer(text, reply_markup=inline.check_nft_status(language[4]))
                elif status == "Unpaid":
                    text = await users.get_text('Статус Unpaid у NFT', language[4])
                    try:
                        await msg.bot.delete_message(msg.chat.id, start_message.message_id)
                    except MessageToDeleteNotFound:
                        pass
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
                        language = await users.user_data(msg.from_user.id)
                        text = "Загружаю NFT..."
                        if language[4] == 'EN':
                            text = "Loading NFT..."
                        start_message = await msg.answer(text)
                        email_ad = await users.check_email(msg.from_user.id)
                        invite_link = await msg.bot.create_chat_invite_link(chat_id=decouple.config('J2M_CHAT'))
                        text = await users.get_text('Успешная покупка NFT (1000)', language[4])
                        text = text.replace('{номер}', f'{dao[0]}').replace('{ссылка}', f'{invite_link.invite_link}')
                        email_text = await users.get_text('Успешная покупка NFT (email)', language[4])
                        email_text = email_text.replace('{номер}', f'{dao[0]}').replace("{адрес}",
                                                                                        f'{address}').replace(
                            "{ключ}", f'{private_key}')
                        if language[4] == "EN":
                            video = decouple.config("NFT_ANIMATION_EN")
                        await send_email_message(to=email_ad[0],
                                                 subject="DAO J2M Smart Contract",
                                                 message_text=email_text)
                        try:
                            await msg.bot.delete_message(msg.chat.id, start_message.message_id)
                        except MessageToDeleteNotFound:
                            pass
                        await msg.answer_video(video=video,
                                               caption=text, reply_markup=inline.main_menu_short(language[4]))
                    else:
                        text = await users.get_text('Ошибка покупки NFT', language[4])
                    try:
                        await msg.bot.delete_message(msg.chat.id, start_message.message_id)
                    except MessageToDeleteNotFound:
                        pass
                    await msg.answer(text, reply_markup=inline.main_menu_short(language[4]))
                elif status == "Rejected":
                    text = await users.get_text('Статус Rejected у NFT', language[4])
                    try:
                        await msg.bot.delete_message(msg.chat.id, start_message.message_id)
                    except MessageToDeleteNotFound:
                        pass
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
            language = await users.user_data(msg.from_user.id)
            text = "Загружаю главное меню..."
            if language[4] == 'EN':
                text = "Loading main menu..."
            start_message = await msg.answer(text)
            try:
                await msg.bot.delete_message(msg.chat.id, start_message.message_id)
            except MessageToDeleteNotFound:
                pass
            await msg.answer("Привет, создатель! 💋")
        else:
            language = await users.user_data(msg.from_user.id)
            text = "Загружаю главное меню..."
            if language[4] == 'EN':
                text = "Loading main menu..."
            start_message = await msg.answer(text)
            try:
                await msg.bot.delete_message(msg.chat.id, start_message.message_id)
            except MessageToDeleteNotFound:
                pass
            await msg.answer("Ой, я не умею работать в группе 😰"
                             f"\n{msg.from_user.full_name}, ты можешь поблагодарить @Caramba и @miroshnikov за создание"
                             f" меня!")


async def nft_start(msg: types.Message):
    language = await users.user_data(msg.from_user.id)
    try:
        ref_tg = await referral.get_id_from_line_1_id(msg.from_user.id)
        ref_full_name = await users.get_tg_full_name(ref_tg[0])
    except TypeError:
        ref_tg = None
        ref_full_name = None
    if ref_tg:
        text = await users.get_text('Сообщение, отправляемое после верификации email (реферал)', language[4])
        text = text.replace("{имя реферала}", f"{ref_full_name}")
        await msg.answer(text, reply_markup=inline.yesno_refill(language[4]))
    else:
        text = await users.get_text('Сообщение, отправляемое после верификации email (нет реферала)', language[4])
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
        text = await users.get_text('Сообщение, отправляемое после верификации email (реферал)', language[4])
        text = text.replace("{имя реферала}", f"{ref_full_name}")
        await call.message.answer(text, reply_markup=inline.yesno_refill(language[4]))
    else:
        text = await users.get_text('Сообщение, отправляемое после верификации email (нет реферала)', language[4])
        await call.message.answer(text, reply_markup=inline.yesno_refill(language[4]))
    await SmartContract.mint_nft.set()


async def bot_start_call(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = "Загружаю главное меню..."
    if language[4] == 'EN':
        text = "Loading main menu..."
    start_message = await call.message.answer(text)
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
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
        try:
            await call.message.bot.delete_message(call.message.chat.id, start_message.message_id)
        except MessageToDeleteNotFound:
            pass
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
            try:
                await call.message.bot.delete_message(call.message.chat.id, start_message.message_id)
            except MessageToDeleteNotFound:
                pass
            await call.message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=inline.main_menu_short(language[4]))
        else:
            language = await users.user_data(call.from_user.id)
            invoiceId = await nft.check_nft_status(call.from_user.id)
            status, title = await thedex.invoice_one(invoiceId[5])
            if status == "Waiting":
                text = await users.get_text('Статус Waiting у NFT', language[4])
                try:
                    await call.message.bot.delete_message(call.message.chat.id, start_message.message_id)
                except MessageToDeleteNotFound:
                    pass
                await call.message.answer(text, reply_markup=inline.check_nft_status(language[4]))
            elif status == "Unpaid":
                text = await users.get_text('Статус Unpaid у NFT', language[4])
                try:
                    await call.message.bot.delete_message(call.message.chat.id, start_message.message_id)
                except MessageToDeleteNotFound:
                    pass
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
                    text = await users.get_text('Успешная покупка NFT (1000)', language[4])
                    text = text.replace('{номер}', f'{dao[0]}').replace('{ссылка}', f'{invite_link.invite_link}')
                    email_text = await users.get_text('Успешная покупка NFT (email)', language[4])
                    email_text = email_text.replace('{номер}', f'{dao[0]}').replace("{адрес}", f'{address}').replace(
                        "{ключ}", f'{private_key}')
                    if language[4] == "EN":
                        video = decouple.config("NFT_ANIMATION_EN")
                    await send_email_message(to=email_ad[0],
                                             subject="DAO J2M Smart Contract",
                                             message_text=email_text)
                    try:
                        await call.message.bot.delete_message(call.message.chat.id, start_message.message_id)
                    except MessageToDeleteNotFound:
                        pass
                    await call.message.answer_video(
                        video=video, caption=text, reply_markup=inline.main_menu_short(language[4]))
                    await call.bot.send_message(
                        chat_id=decouple.config('GROUP_ID'),
                        text=f"Пользователь {call.from_user.id} - {call.from_user.username} получил NFT (РЕКЛАМА)"
                             f"\n\nПодробнее по ссылке: http://89.223.121.160:8000/admin/app/nft/")
                else:
                    text = "Произошла ошибка, обратитесь в поддержку"
                    if language[4] == "EN":
                        text = "An error occurred. Please contact support."
                try:
                    await call.message.bot.delete_message(call.message.chat.id, start_message.message_id)
                except MessageToDeleteNotFound:
                    pass
                await call.message.answer(text, reply_markup=inline.main_menu_short(language[4]))
            elif status == "Rejected":
                text = await users.get_text('Статус Rejected у NFT', language[4])
                try:
                    await call.message.bot.delete_message(call.message.chat.id, start_message.message_id)
                except MessageToDeleteNotFound:
                    pass
                await call.message.answer(text)
                await nft.delete_error(call.from_user.id)
    elif not user_status:
        try:
            await call.message.bot.delete_message(call.message.chat.id, start_message.message_id)
        except MessageToDeleteNotFound:
            pass
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
    text = await users.get_text('Главное меню поддержки (1000)', language[4])
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
    except MessageToDeleteNotFound:
        pass
    transaction = await thedex_db.get_transaction(call.from_user.id)
    try:
        transaction = transaction[0]
        await thedex_db.delete_transaction(transaction[0])
    except MessageToDeleteNotFound:
        pass
    photo = decouple.config('BANNER_MAIN')
    text = "Транзакция успешно отменена!"
    if language[4] == "EN":
        text = "Transaction successfully canceled!"
        photo = decouple.config('BANNER_MAIN_EN')
    await call.message.answer_photo(photo=photo, caption=text,
                                    reply_markup=await inline.main_menu(language[4], call.from_user.id))


async def email(msg: types.Message):
    language = await users.user_data(msg.from_user.id)
    try:
        await msg.delete()
    except MessageToDeleteNotFound:
        pass
    text = await users.get_text('Приветственное сообщение #3', language[4])
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
        text = await users.get_text("Подтверждение кода из email", language[4])
        text = text.replace("{здесь email}", f"{msg.text}")
        email_text = await users.get_text('Сообщение, отправляемое по email #1', language[4])
        email_text = email_text.replace("{здесь код}", f'{code}')
        await send_email_message(to=msg.text,
                                 subject="DAO J2M verification",
                                 message_text=email_text)
        await msg.answer(text)
        await Email.next()
    else:
        text = await users.get_text('Ошибка при формате почты', language[4])
        await msg.answer(text)


async def ver_code(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        language = await users.user_data(msg.from_user.id)
        if msg.text == data.get("code"):
            text = await users.get_text('Успешный код верификации', language[4])
            await msg.answer(text)
            await users.insert_email(msg.from_id, data.get('email'))
            await bot_start(msg, state)
        else:
            text = await users.get_text('Ошибка кода верификации', language[4])
            await msg.answer(text, reply_markup=inline.email_verif(language[4]))
            await Email.next()


async def one_more(call: types.CallbackQuery, state: FSMContext):
    language = await users.user_data(call.from_user.id)
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass
    if call.data == "new_code":
        async with state.proxy() as data:
            code = generate_random_code()
            await state.update_data({"code": code})
            text = await users.get_text("Подтверждение кода из email", language[4])
            text = text.replace("{здесь email}", "")
            email_text = await users.get_text('Сообщение, отправляемое по email #1', language[4])
            email_text = email_text.replace("{здесь код}", f'{code}')
            await send_email_message(to=data.get('email'),
                                     subject="DAO J2M verification",
                                     message_text=email_text)
            await call.message.answer(text)
            await state.set_state(Email.ver_code.state)
    if call.data == "change_email":
        text = await users.get_text('Приветственное сообщение #3', language[4])
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
