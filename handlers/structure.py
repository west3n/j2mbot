import asyncio

import decouple
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards import inline
from database import users, referral, balance, structure, nft


class UserForm(StatesGroup):
    accept = State()
    name = State()
    socials = State()
    finish = State()


class ChangeForm(StatesGroup):
    name = State()
    socials = State()


async def structure_handler(call: types.CallbackQuery):
    status = await balance.get_balance_history(call.from_user.id, "IN")
    language = await users.user_data(call.from_user.id)
    try:
        await call.message.delete()
    except:
        pass
    # try:
    #     status = status[0]
    # except TypeError:
    #     status = None
    if status:
        await call.bot.send_chat_action(call.message.chat.id, "typing")
        photo = decouple.config("BANNER_STRUCTURE")
        user_form = await structure.get_user_form(call.from_user.id)
        if not user_form:
            text = 'Для участия в партнерской программе, вам нужно ознакомится с правилами программы, подтвердить' \
                   ' Ваше согласие на участие, а также заполнить анкету участника.'
            text_2 = 'Принимаете правила партнерской программы?'
            document = decouple.config("AFFILIATE_PROGRAM")
            if language[4] == "EN":
                text = "To participate in the affiliate program, you need to familiarize yourself with the program's " \
                       "rules, confirm your agreement to participate, and fill out the participant form."
                text_2 = "Do you accept the rules of the affiliate program?"
                document = decouple.config("AFFILIATE_PROGRAM_EN")

            await call.message.answer(text)
            await call.bot.send_chat_action(call.message.chat.id, "upload_document")
            await asyncio.sleep(2)
            await call.message.answer_document(document)
            await call.bot.send_chat_action(call.message.chat.id, "typing")
            await asyncio.sleep(2)
            await call.message.answer(text_2, reply_markup=inline.user_terms(language[4]))
            await UserForm.accept.set()
        else:
            ref_tg = await referral.get_id_from_line_1_id(call.from_user.id)
            ref_balance = await balance.get_balance_status(call.from_user.id)
            try:
                ref_balance = ref_balance[5]
            except:
                ref_balance = 0

            text_x = ""
            text_x_e = ""
            ref_line_1 = await referral.get_line_1(call.from_user.id)
            try:
                ref_line_1 = ref_line_1[0]
            except:
                ref_line_1 = 0
            ref_line_2 = await referral.get_line_2(call.from_user.id)
            try:
                ref_line_2 = ref_line_2[0]
            except:
                ref_line_2 = 0
            ref_line_3 = await referral.get_line_3(call.from_user.id)
            try:
                ref_line_3 = ref_line_3[0]
            except:
                ref_line_3 = 0

            if ref_tg:
                ref_name = await users.get_tg_username(ref_tg[0])
                text_x = f"\n*Вас пригласил:* _@{ref_name}_"
                text_x_e = f"\n*You were invited by:* _@{ref_name}_"

            text = f"*Ваш ID:* _{call.from_user.id}_" \
                   f"{text_x}" \
                   f"\n*Ваша партнёрская ссылка: \(нажмите на неё, чтобы скопировать\)*" \
                   f"\n`https://t.me/DAO_J2M_bot?start={call.from_user.id}`" \
                   f"\n\n*Всего заработано за весь период:* _{ref_balance} USDT_" \
                   f"\n\n╔ *1 Линия*  Количество человек: _{ref_line_1}_" \
                   f"\n╟ Оборот: _0 USDT_" \
                   f"\n╟ *2 Линия*  Количество человек: _{ref_line_2}_" \
                   f"\n╟ Оборот: _0 USDT_" \
                   f"\n╟ *3 Линия*  Количество человек: _{ref_line_3}_" \
                   f"\n╚ Оборот: _0 USDT_" \
                   f"\n\n_❔ Подробно о том, как начисляются бонусы можно узнать в разделе 'Информация'_"

            if language[4] == 'EN':
                photo = decouple.config("BANNER_STRUCTURE_EN")
                text = f"*Your ID:* _{call.from_user.id}_" \
                       f"{text_x_e}" \
                       f"\n*Your referral link: \(press it for copying\)* " \
                       f"\n`https://t.me/J2M_devbot?start={call.from_user.id}`" \
                       f"\n\n*Total earned for the entire period:* _{ref_balance} USDT_" \
                       f"\n\n╔ *1 Line* Number of people: _{ref_line_1}_ " \
                       f"\n╟ Turnover: _0 USDT_" \
                       f"\n╟ *2 Line* Number of people: _{ref_line_2}_ " \
                       f"\n╟ Turnover: _0 USDT_" \
                       f"\n╟ *3 Line* Number of people: _{ref_line_3}_ " \
                       f"\n╚ Turnover: _0 USDT_" \
                       f"\n\n_❔ For detailed information on how bonuses are calculated, " \
                       f"please refer to the 'Information' section_"

            await call.message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=inline.referral_statistic(language[4]),
                parse_mode=types.ParseMode.MARKDOWN_V2)
    else:
        photo = decouple.config("BANNER_MAIN")
        text = "Для принятия участия в партнерской программе J2M необходимо пополнить баланс. " \
               "Подробнее в разделе 'Пополнение'"
        if language[4] == "EN":
            photo = decouple.config("BANNER_MAIN_EN")
            text = "To participate in the J2M affiliate program, you need to replenish your balance. "
            "For more details, please refer to the 'Replenishment' section."
        await call.message.answer_photo(photo=photo, caption=text,
                                        reply_markup=await inline.main_menu(language[4], call.from_user.id))


async def structure_handler_msg(msg: types.Message):
    photo = decouple.config("BANNER_STRUCTURE")
    await msg.bot.send_chat_action(msg.chat.id, "typing")
    language = await users.user_data(msg.from_user.id)
    ref_tg = await referral.get_id_from_line_1_id(msg.from_user.id)
    ref_balance = await balance.get_balance_status(msg.from_user.id)
    try:
        ref_balance = ref_balance[5]
    except:
        ref_balance = 0

    text_x = ""
    text_x_e = ""
    ref_line_1 = await referral.get_line_1(msg.from_user.id)
    try:
        ref_line_1 = ref_line_1[0]
    except:
        ref_line_1 = 0
    ref_line_2 = await referral.get_line_2(msg.from_user.id)
    try:
        ref_line_2 = ref_line_2[0]
    except:
        ref_line_2 = 0
    ref_line_3 = await referral.get_line_3(msg.from_user.id)
    try:
        ref_line_3 = ref_line_3[0]
    except:
        ref_line_3 = 0

    if ref_tg:
        ref_name = await users.get_tg_username(ref_tg[0])
        text_x = f"\n*Вас пригласил:* _@{ref_name}_"
        text_x_e = f"\n*You were invited by:* _@{ref_name}_"

    text = f"*Ваш ID:* _{msg.from_user.id}_" \
           f"{text_x}" \
           f"\n*Ваша партнёрская ссылка: \(нажмите на неё, чтобы скопировать\)*" \
           f"\n`https://t.me/DAO_J2M_bot?start={msg.from_user.id}`" \
           f"\n\n*Всего заработано за весь период:* _{ref_balance} USDT_" \
           f"\n\n╔ *1 Линия*  Количество человек: _{ref_line_1}_" \
           f"\n╟ Оборот: _0 USDT_" \
           f"\n╟ *2 Линия*  Количество человек: _{ref_line_2}_" \
           f"\n╟ Оборот: _0 USDT_" \
           f"\n╟ *3 Линия*  Количество человек: _{ref_line_3}_" \
           f"\n╚ Оборот: _0 USDT_" \
           f"\n\n_❔ Подробно о том, как начисляются бонусы можно узнать в разделе 'Информация'_"

    if language[4] == 'EN':
        photo = decouple.config("BANNER_STRUCTURE_EN")
        text = f"*Your ID:* _{msg.from_user.id}_" \
               f"{text_x_e}" \
               f"\n*Your referral link: \(press it for copying\)* " \
               f"\n`https://t.me/J2M_devbot?start={msg.from_user.id}`" \
               f"\n\n*Total earned for the entire period:* _{ref_balance} USDT_" \
               f"\n\n╔ *1 Line* Number of people: _{ref_line_1}_ " \
               f"\n╟ Turnover: _0 USDT_" \
               f"\n╟ *2 Line* Number of people: _{ref_line_2}_ " \
               f"\n╟ Turnover: _0 USDT_" \
               f"\n╟ *3 Line* Number of people: _{ref_line_3}_ " \
               f"\n╚ Turnover: _0 USDT_" \
               f"\n\n_❔ For detailed information on how bonuses are calculated, " \
               f"please refer to the 'Information' section_"

    await msg.delete()
    await msg.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=inline.referral_statistic(language[4]),
        parse_mode=types.ParseMode.MARKDOWN_V2)


async def handle_user_terms_kb(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=inline.user_terms_2(language[4]))
    await UserForm.next()


async def handle_name(call: types.CallbackQuery):
    await call.message.delete()
    language = await users.user_data(call.from_user.id)
    text = 'Напишите ваше ФИО полностью:'
    if language[4] == "EN":
        text = "Please write your full name:"
    await call.message.answer(text)
    await UserForm.next()


async def handle_socials(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['name'] = msg.text
    text = 'Отправьте ссылки на ваши соц. сети и информационные ресурсы одним сообщением, каждое с новой строки:'
    if language[4] == "EN":
        text = "Please send the links to your social media profiles and informational " \
               "resources in a single message, with each link on a new line:"
    await msg.answer(text)
    await UserForm.next()


async def save_form(msg: types.Message, state: FSMContext):
    user_id = await nft.nft_id(msg.from_user.id)
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['socials'] = msg.text
    text = f'Анкета заполнена. \n\nВаш индивидуальный номер в партнерской программе: {user_id}' \
           f'\n\nВаша персональная ссылка-приглашение: https://t.me/DAO_J2M_bot?start={msg.from_user.id}' \
           f'\n\nИзменить данные анкеты Вы сможете в дальнейшем в этом меню.'
    if language[4] == "EN":
        text = f"The form has been completed. " \
               f"\n\nYour individual number in the affiliate program: {user_id}" \
               f"\n\nYour personal invitation link: https://t.me/DAO_J2M_bot?start={msg.from_user.id}" \
               f"\n\nYou will be able to update your form data in this menu in the future."
    await msg.answer(text)
    await structure.save_user_form(data.get('name'), data.get('socials'), msg.from_id)
    await state.finish()
    await structure_handler_msg(msg)


async def full_statistic(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = "Узнайте подробную статистику своих рефералов"
    if language[4] == "EN":
        text = "Get detailed statistics about your referrals."
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.referral_lines(language[4]))


async def all_referral_lines(call: types.CallbackQuery):
    await call.bot.send_chat_action(call.message.chat.id, 'typing')
    language = await users.user_data(call.from_user.id)
    all_line_ids = []
    text = ''
    if call.data == "line1":
        all_line_ids = await referral.get_line_1(call.from_user.id)
    elif call.data == 'line2':
        all_line_ids = await referral.get_line_2(call.from_user.id)
    elif call.data == 'line3':
        all_line_ids = await referral.get_line_3(call.from_user.id)
    if all_line_ids[1]:
        for tg_id in all_line_ids[1]:
            user_name = await users.get_tg_username(tg_id)
            if user_name:
                deposit_balance, referral_balance = await balance.get_balance_line(tg_id)
                text += f"• {tg_id} (@{user_name}) | {deposit_balance} USDT | {referral_balance} USDT\n"
            else:
                pass
    else:
        text += "У вас нет рефералов по этой линии" if language[4] == "RU" else "You have no referrals for that line"
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.detailed_statistic(language[4]))


async def handle_user_data(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    user_data = await structure.get_user_form(call.from_user.id)
    text = f'Ваше имя: {user_data[1]}\n\nUsername: {call.from_user.username}\n\nСоц.сети: {user_data[2]}' \
           f'\n\nЧтобы изменить неактуальную информацию, нажмите соответствующую кнопку ниже.'
    if language[4] == "EN":
        text = f"Your name: {user_data[1]}\n\nUsername: {call.from_user.username}\n\nSocial media: {user_data[2]}" \
               "\n\nTo update outdated information, click the corresponding button below."
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.change_data(language[4]))


async def change_user_data(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'change_name':
        text = 'Введите новое имя:'
        if language[4] == "EN":
            text = 'Input new full name:'
        await call.message.edit_text(text)
        await ChangeForm.name.set()
    elif call.data == 'change_socials':
        text = 'Введите новые соц.сети:'
        if language[4] == "EN":
            text = 'Input new socials:'
        await call.message.edit_text(text)
        await ChangeForm.socials.set()


async def handle_name_change(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['name'] = msg.text
    await structure.update_name(msg.from_id, data.get('name'))
    text = 'Данные успешно обновлены!'
    if language[4] == "EN":
        text = 'Data successfully updated!'
    await msg.answer(text, reply_markup=inline.referral_statistic(language[4]))
    await state.finish()


async def handle_socials_change(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['social'] = msg.text
    await structure.update_socials(msg.from_id, data.get('social'))
    text = 'Данные успешно обновлены!'
    if language[4] == "EN":
        text = 'Data successfully updated!'
    await msg.answer(text, reply_markup=inline.referral_statistic(language[4]))
    await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(structure_handler, text='structure')
    dp.register_callback_query_handler(handle_user_terms_kb, state=UserForm.accept)
    dp.register_callback_query_handler(handle_name, state=UserForm.name)
    dp.register_message_handler(handle_socials, state=UserForm.socials)
    dp.register_message_handler(save_form, state=UserForm.finish)
    dp.register_callback_query_handler(full_statistic, text='full_statistic')
    dp.register_callback_query_handler(all_referral_lines, lambda c: c.data in ['line1', 'line2', 'line3'])
    dp.register_callback_query_handler(handle_user_data, text='user_data')
    dp.register_callback_query_handler(change_user_data, lambda c: c.data in ['change_name', 'change_socials'])
    dp.register_message_handler(handle_name_change, state=ChangeForm.name)
    dp.register_message_handler(handle_socials_change, state=ChangeForm.socials)
