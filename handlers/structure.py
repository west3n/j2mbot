import asyncio
import decouple

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound

from keyboards import inline
from database import users, referral, balance, structure, nft, stabpool


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
    except MessageToDeleteNotFound:
        pass
    if status:
        await call.bot.send_chat_action(call.message.chat.id, "typing")
        photo = decouple.config("BANNER_STRUCTURE")
        user_form = await structure.get_user_form(call.from_user.id)
        if not user_form:
            text = await users.get_text("Партнерская программа регистрация", language[4])
            text_2 = await users.get_text("Партнерская программа регистрация №2", language[4])
            document = decouple.config("AFFILIATE_PROGRAM")
            if language[4] == "EN":
                document = decouple.config("AFFILIATE_PROGRAM_EN")
            await call.message.answer(text)
            await call.bot.send_chat_action(call.message.chat.id, "upload_document")
            await asyncio.sleep(1)
            await call.message.answer_document(document)
            await call.bot.send_chat_action(call.message.chat.id, "typing")
            await asyncio.sleep(1)
            await call.message.answer(text_2, reply_markup=inline.user_terms(language[4]))
            await UserForm.accept.set()
        else:
            collective_sum = await balance.get_collective_refill_sum(call.from_user.id)
            ref_tg = await referral.get_id_from_line_1_id(call.from_user.id)
            ref_balance = await balance.get_balance(call.from_user.id)
            try:
                ref_balance = ref_balance[3]
                if "." in str(ref_balance):
                    ref_balance = str(ref_balance).replace(".", ",")
            except TypeError:
                ref_balance = 0

            text_x = ""
            text_x_e = ""
            balance_line_1 = 0
            ref_line_1 = await referral.get_line_1(call.from_user.id)
            for ref_user in ref_line_1[1]:
                try:
                    ref_user_balance = await balance.get_balance_(ref_user)
                    ref_user_balance = float(ref_user_balance[0]) + float(ref_user_balance[1])
                except:
                    ref_user_balance = 0
                try:
                    stabpool_user_balance = await stabpool.get_balance(ref_user)
                    stabpool_user_balance = float(stabpool_user_balance[0] + float(stabpool_user_balance[1]))
                except:
                    stabpool_user_balance = 0
                balance_line_1 += round(ref_user_balance, 2)
                balance_line_1 += round(stabpool_user_balance, 2)
            try:
                ref_line_1 = ref_line_1[0]
            except TypeError:
                ref_line_1 = 0
            balance_line_2 = 0
            ref_line_2 = await referral.get_line_2(call.from_user.id)
            for ref_user in ref_line_2[1]:
                try:
                    ref_user_balance = await balance.get_balance_(ref_user)
                    ref_user_balance = float(ref_user_balance[0]) + float(ref_user_balance[1])
                except:
                    ref_user_balance = 0
                try:
                    stabpool_user_balance = await stabpool.get_balance(ref_user)
                    stabpool_user_balance = float(stabpool_user_balance[0] + float(stabpool_user_balance[1]))
                except:
                    stabpool_user_balance = 0
                balance_line_2 += round(ref_user_balance, 2)
                balance_line_2 += round(stabpool_user_balance, 2)
            try:
                ref_line_2 = ref_line_2[0]
            except TypeError:
                ref_line_2 = 0
            balance_line_3 = 0
            ref_line_3 = await referral.get_line_3(call.from_user.id)
            for ref_user in ref_line_3[1]:
                try:
                    ref_user_balance = await balance.get_balance_(ref_user)
                    ref_user_balance = float(ref_user_balance[0]) + float(ref_user_balance[1])
                except:
                    ref_user_balance = 0
                try:
                    stabpool_user_balance = await stabpool.get_balance(ref_user)
                    stabpool_user_balance = float(stabpool_user_balance[0] + float(stabpool_user_balance[1]))
                except:
                    stabpool_user_balance = 0
                balance_line_3 += round(ref_user_balance, 2)
                balance_line_3 += round(stabpool_user_balance, 2)
            try:
                ref_line_3 = ref_line_3[0]
            except TypeError:
                ref_line_3 = 0
            special_chars = ['.', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '!', ':']
            if ref_tg:
                ref_name = await users.get_tg_username(ref_tg[0])
                invitor_data = await structure.get_user_form(ref_tg[0])
                text_x = f"\n\n‍👦*Вас пригласил:* _@{ref_name}_"
                text_x_e = f"\n\n👨‍👦 *You were invited by:* _@{ref_name}_"
                if invitor_data:
                    text_x += f"\n   ↳ _Имя_: {invitor_data[1]}" \
                              f"\n   ↳ _Социальные сети_: {invitor_data[2]}"
                    text_x_e += f"\n   ↳ _Name_: {invitor_data[1]}" \
                                f"\n   ↳ _Social media_: {invitor_data[2]}"
            text = f"🆔 *Ваш ID:* `{call.from_user.id}`" \
                   f"{text_x}" \
                   f"\n\n🔗 *Ваша партнёрская ссылка:*" \
                   f"\n`https://t.me/DAO_J2M_bot?start={call.from_user.id}`" \
                   f"\n\n*Партнёрские начисления за весь период:* _{ref_balance} USDT_" \
                   f"\n\n*1 Линия:*  " \
                   f"\n ↳ _Количество человек_: _{ref_line_1}_" \
                   f"\n ↳ _Оборот_: {balance_line_1} USDT"
            if collective_sum >= 500:
                text += f"\n*2 Линия:*  " \
                        f"\n ↳ _Количество человек_: _{ref_line_2}_" \
                        f"\n ↳ _Оборот_: {balance_line_2} USDT"
            else:
                text += "\n*2 Линия станет доступна после пополнения от 500 USD*"
            if collective_sum >= 1000:
                text += f"\n*3 Линия:* " \
                        f"\n ↳ _Количество человек_: _{ref_line_3}_" \
                        f"\n ↳ _Оборот_: {balance_line_3} USDT"
            else:
                text += f"\n*3 Линия станет доступна после пополнения от 1000 USD*"
            text += f"\n\n_❔ Подробно о том, как начисляются бонусы можно узнать в разделе 'Информация'_"
            for char in special_chars:
                text = text.replace(char, "\\" + char)
            if language[4] == 'EN':
                photo = decouple.config("BANNER_STRUCTURE_EN")
                text = f"*Your ID:* `{call.from_user.id}`" \
                       f"{text_x_e}" \
                       f"\n*Your referral link: (press it for copying)* " \
                       f"\n`https://t.me/J2M_devbot?start={call.from_user.id}`" \
                       f"\n\n*Total earned for the entire period:* _{ref_balance} USDT_" \
                       f"\n\n*1 Line:* " \
                       f"\n ↳ Number of people: _{ref_line_1}_ " \
                       f"\n ↳ Turnover: _{balance_line_1} USDT_"
                if collective_sum >= 500:
                    text += f"\n*2 Line:* " \
                            f"\n ↳ Number of people: _{ref_line_2}_ " \
                            f"\n ↳ Turnover: _{balance_line_2} USDT_"
                else:
                    text += "\n*Line 2 will be available after refill more than 500 USD*"
                if collective_sum >= 1000:
                    text += f"\n*3 Line:*" \
                            f"\n ↳ Number of people: _{ref_line_3}_ " \
                            f"\n ↳ Turnover: _{balance_line_3} USDT_"
                else:
                    text += "\n*Line 3 will be available after refill more than 1000 USD*"
                text += f"\n\n_❔ For detailed information on how bonuses are calculated, " \
                        f"please refer to the 'Information' section_"
                for char in special_chars:
                    text = text.replace(char, "\\" + char)
            try:
                await call.message.delete()
            except MessageToDeleteNotFound:
                pass
            await call.message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=inline.referral_statistic(language[4]),
                parse_mode=types.ParseMode.MARKDOWN_V2)
    else:
        photo = decouple.config("BANNER_MAIN")
        text = await users.get_text("Партнерская программа регистрация ошибка (1000)", language[4])
        if language[4] == "EN":
            photo = decouple.config("BANNER_MAIN_EN")
        await call.message.answer_photo(photo=photo, caption=text,
                                        reply_markup=await inline.main_menu(language[4], call.from_user.id))


async def structure_handler_msg(msg: types.Message):
    photo = decouple.config("BANNER_STRUCTURE")
    await msg.bot.send_chat_action(msg.chat.id, "typing")
    language = await users.user_data(msg.from_user.id)
    ref_tg = await referral.get_id_from_line_1_id(msg.from_user.id)
    ref_balance = await balance.get_balance(msg.from_user.id)
    try:
        ref_balance = ref_balance[3]
        if "." in str(ref_balance):
            ref_balance = str(ref_balance).replace(".", ",")
    except TypeError:
        ref_balance = 0

    text_x = ""
    text_x_e = ""
    balance_line_1 = 0
    ref_line_1 = await referral.get_line_1(msg.from_user.id)
    for ref_user in ref_line_1[1]:
        try:
            ref_user_balance = await balance.get_balance_(ref_user)
            ref_user_balance = float(ref_user_balance[0]) + float(ref_user_balance[1])
        except:
            ref_user_balance = 0
        try:
            stabpool_user_balance = await stabpool.get_balance(ref_user)
            stabpool_user_balance = float(stabpool_user_balance[0] + float(stabpool_user_balance[1]))
        except:
            stabpool_user_balance = 0
        balance_line_1 += round(ref_user_balance, 2)
        balance_line_1 += round(stabpool_user_balance, 2)
    try:
        ref_line_1 = ref_line_1[0]
    except TypeError:
        ref_line_1 = 0
    balance_line_2 = 0
    ref_line_2 = await referral.get_line_2(msg.from_user.id)
    for ref_user in ref_line_2[1]:
        try:
            ref_user_balance = await balance.get_balance_(ref_user)
            ref_user_balance = float(ref_user_balance[0]) + float(ref_user_balance[1])
        except:
            ref_user_balance = 0
        try:
            stabpool_user_balance = await stabpool.get_balance(ref_user)
            stabpool_user_balance = float(stabpool_user_balance[0] + float(stabpool_user_balance[1]))
        except:
            stabpool_user_balance = 0
        balance_line_2 += round(ref_user_balance, 2)
        balance_line_2 += round(stabpool_user_balance, 2)
    try:
        ref_line_2 = ref_line_2[0]
    except TypeError:
        ref_line_2 = 0
    balance_line_3 = 0
    ref_line_3 = await referral.get_line_3(msg.from_user.id)
    for ref_user in ref_line_3[1]:
        try:
            ref_user_balance = await balance.get_balance_(ref_user)
            ref_user_balance = float(ref_user_balance[0]) + float(ref_user_balance[1])
        except:
            ref_user_balance = 0
        try:
            stabpool_user_balance = await stabpool.get_balance(ref_user)
            stabpool_user_balance = float(stabpool_user_balance[0] + float(stabpool_user_balance[1]))
        except:
            stabpool_user_balance = 0
        balance_line_3 += round(ref_user_balance, 2)
        balance_line_3 += round(stabpool_user_balance, 2)
    try:
        ref_line_3 = ref_line_3[0]
    except TypeError:
        ref_line_3 = 0
    special_chars = ['.', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '!', ':']
    if ref_tg:
        ref_name = await users.get_tg_username(ref_tg[0])
        invitor_data = await structure.get_user_form(ref_tg[0])
        text_x = f"\n\n‍👦*Вас пригласил:* _@{ref_name}_"
        if invitor_data:
            text_x += f"\n   ↳ _Имя_: {invitor_data[1]}" \
                      f"\n   ↳ _Социальные сети_: {invitor_data[2]}"
            text_x_e += f"\n   ↳ _Name_: {invitor_data[1]}" \
                        f"\n   ↳ _Social media_: {invitor_data[2]}"
        text_x_e = f"\n\n👨‍👦 *You were invited by:* _@{ref_name}_"
    text = f"🆔 *Ваш ID:* `{msg.from_user.id}`" \
           f"{text_x}" \
           f"\n\n🔗 *Ваша партнёрская ссылка:*" \
           f"\n`https://t.me/DAO_J2M_bot?start={msg.from_user.id}`" \
           f"\n\n*Партнёрские начисления за весь период:* _{ref_balance} USDT_" \
           f"\n\n*1 Линия:*  " \
           f"\n ↳ _Количество человек_: _{ref_line_1}_" \
           f"\n ↳ _Оборот_: {balance_line_1} USDT" \
           f"\n*2 Линия:*  " \
           f"\n ↳ _Количество человек_: _{ref_line_2}_" \
           f"\n ↳ _Оборот_: {balance_line_2} USDT" \
           f"\n*3 Линия:*  " \
           f"\n ↳ _Количество человек_: _{ref_line_3}_" \
           f"\n ↳ _Оборот_: {balance_line_3} USDT" \
           f"\n\n_❔ Подробно о том, как начисляются бонусы можно узнать в разделе 'Информация'_"
    for char in special_chars:
        text = text.replace(char, "\\" + char)
    if language[4] == 'EN':
        photo = decouple.config("BANNER_STRUCTURE_EN")
        text = f"*Your ID:* `{msg.from_user.id}`" \
               f"{text_x_e}" \
               f"\n*Your referral link: (press it for copying)* " \
               f"\n`https://t.me/J2M_devbot?start={msg.from_user.id}`" \
               f"\n\n*Total earned for the entire period:* _{ref_balance} USDT_" \
               f"\n\n*1 Line:* " \
               f"\n ↳ Number of people: _{ref_line_1}_ " \
               f"\n ↳ Turnover: _{balance_line_1} USDT_" \
               f"\n*2 Line:* " \
               f"\n ↳ Number of people: _{ref_line_2}_ " \
               f"\n ↳ Turnover: _{balance_line_2} USDT_" \
               f"\n*3 Line:*" \
               f"\n ↳ Number of people: _{ref_line_3}_ " \
               f"\n ↳ Turnover: _{balance_line_3} USDT_" \
               f"\n\n_❔ For detailed information on how bonuses are calculated, " \
               f"please refer to the 'Information' section_"
        for char in special_chars:
            text = text.replace(char, "\\" + char)
    try:
        await msg.delete()
    except MessageToDeleteNotFound:
        pass
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
    text = await users.get_text("Анкета имя", language[4])
    await call.message.answer(text)
    await UserForm.next()


async def handle_socials(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['name'] = msg.text
    text = await users.get_text("Анкета социальные сети", language[4])
    await msg.answer(text)
    await UserForm.next()


async def save_form(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['socials'] = msg.text
    text = await users.get_text("Анкета сохранение", language[4])
    await msg.answer(text)
    await structure.save_user_form(data.get('name'), data.get('socials'), msg.from_id)
    await state.finish()
    await structure_handler_msg(msg)


async def full_statistic(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    text = await users.get_text("Подробная статистика рефералов", language[4])
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
            print(tg_id)
            try:
                user_name = await users.get_tg_username(tg_id)
            except TypeError:
                user_name = None
            if user_name:
                try:
                    deposit_balance, referral_balance = await balance.get_balance_line(tg_id)
                    text += f"• [Коллективный аккаунт] {tg_id} (@{user_name}) | {deposit_balance} USDT | {referral_balance} USDT\n"
                except TypeError:
                    text += f"• [Коллективный аккаунт] {tg_id} (@{user_name}) | Пользователь еще не создал кошелек J2M\n"
                    if language[4] == "EN":
                        text += f"• [Collective account] {tg_id} (@{user_name}) | User has not yet entered wallet J2M\n"
                try:
                    deposit_balance, referral_balance = await stabpool.get_balance_line(tg_id)
                    text += f"• [Стабилизационный пул] {tg_id} (@{user_name}) | {deposit_balance} USDT | {referral_balance} USDT\n"
                except TypeError:
                    pass
            else:
                text += f"• {tg_id} (Не зарегистрирован в системе) | Пользователь еще не заключил смарт-контракт\n"
    else:
        text += "У вас нет рефералов по этой линии" if language[4] == "RU" else "You have no referrals for that line"
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.detailed_statistic(language[4]))


async def handle_user_data(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    user_data = await structure.get_user_form(call.from_user.id)
    user_name = f"@{call.from_user.username}" if call.from_user.username else 'Добавьте в настройках Телеграм'
    text = f'<b>🧔 Ваше имя:</b> {user_data[1]}\n\n' \
           f'<b>🪪 Username:</b> {user_name}' \
           f'\n\n<b>🌐 Социальные сети:</b> {user_data[2]}' \
           f'\n\n<em>❔ Чтобы изменить неактуальную информацию, нажмите соответствующую кнопку ниже.</em>'
    if language[4] == "EN":
        user_name = f"@{call.from_user.username}" if call.from_user.username else 'Add username in Telegram settings'
        text = f"Your name: {user_data[1]}\n\nUsername: {user_name}\n\n" \
               f"Social media: {user_data[2]}" \
               "\n\nTo update outdated information, click the corresponding button below."
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.change_data(language[4]))


async def change_user_data(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    if call.data == 'change_name':
        text = await users.get_text("Анкета изменение имя", language[4])
        await call.message.edit_text(text)
        await ChangeForm.name.set()
    elif call.data == 'change_socials':
        text = await users.get_text("Анкета изменение социальные сети", language[4])
        await call.message.edit_text(text)
        await ChangeForm.socials.set()


async def handle_name_change(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['name'] = msg.text
    await structure.update_name(msg.from_id, data.get('name'))
    text = await users.get_text("Анкета изменено имя", language[4])
    await msg.answer(text, reply_markup=inline.referral_statistic(language[4]))
    await state.finish()


async def handle_socials_change(msg: types.Message, state: FSMContext):
    language = await users.user_data(msg.from_user.id)
    async with state.proxy() as data:
        data['social'] = msg.text
    await structure.update_socials(msg.from_id, data.get('social'))
    text = await users.get_text("Анкета изменено социальные сети", language[4])
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
