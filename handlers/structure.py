import asyncio

import decouple
from aiogram import Dispatcher, types
from keyboards import inline
from database import users, referral, balance


async def structure_handler(call: types.CallbackQuery):
    await call.bot.send_chat_action(call.message.chat.id, "typing")
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_STRUCTURE")
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
           f"\n`https://t.me/J2M_invest_bot?start={call.from_user.id}`" \
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

    await call.message.delete()
    await call.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=inline.referral_statistic(language[4]),
        parse_mode=types.ParseMode.MARKDOWN_V2)


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
                deposit_balance = 0
                referral_balance = 0
                text += f"• {tg_id} (@{user_name}) | {deposit_balance} USDT | {referral_balance} USDT\n"
            else:
                pass
    else:
        text += "У вас нет рефералов по этой линии" if language[4] == "RU" else "You have no referrals for that line"
    await call.message.delete()
    await call.message.answer(text, reply_markup=inline.detailed_statistic(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(structure_handler, text='structure')
    dp.register_callback_query_handler(full_statistic, text='full_statistic')
    dp.register_callback_query_handler(all_referral_lines, lambda c: c.data in ['line1', 'line2', 'line3'])
