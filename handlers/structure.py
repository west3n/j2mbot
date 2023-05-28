import decouple
from aiogram import Dispatcher, types
from keyboards import inline
from database import users, referral


async def structure_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    photo = decouple.config("BANNER_STRUCTURE")
    ref_tg = await referral.get_id_from_line_1_id(call.from_user.id)
    text_x = ""
    text_x_e = ""
    if ref_tg:
        ref_name = await users.get_tg_username(ref_tg[0])
        text_x = f"\n<b>Вас пригласил:</b> <em>@{ref_name}</em>"
        text_x_e = f"\n<b>You were invited by:</b> <em>@{ref_name}</em>"

    text = f"<b>Ваш ID:</b> <em>{call.from_user.id}</em>" \
           f"{text_x}"\
           f"\n<b>Ваша партнёрская ссылка:</b> https://t.me/J2M_invest_bot?start={call.from_user.id}" \
           f"\n\n<b>Всего заработано за весь период:</b><em>  USDT</em>" \
           f"\n\n╔ <b>1 Линия.</b>  Кол-во человек: <em>TEST</em> \n╟ Оборот:<em>  USDT</em>" \
           f"\n╟ <b>2 Линия.</b>  Кол-во человек: <em>TEST</em>  \n╟ Оборот:  <em>USDT</em>" \
           f"\n╟ <b>3 Линия.</b>  Кол-во человек: <em>TEST</em>  \n╚ Оборот:  <em>USDT</em>" \
           f"\n\n<em>❔ Подробно о том, как начисляются бонусы можно узнать в разделе 'Информация'</em>"

    if language[4] == 'EN':
        photo = decouple.config("BANNER_STRUCTURE_EN")
        text = f"<b>Your ID:</b> <em>{call.from_user.id}</em>" \
               f"{text_x_e}" \
               f"\n<b>Your referral link:</b> https://t.me/J2M_invest_bot?start={call.from_user.id}" \
               f"\n\n<b>Total earned for the entire period:</b><em>  USDT</em>" \
               f"\n\n<b>1 Line.</b> Number of people: <em>TEST</em> Turnover:<em>  USDT</em>" \
               f"\n<b>2 Line.</b> Number of people: <em>TEST</em> Turnover: <em>USDT</em>" \
               f"\n<b>3 Line.</b> Number of people: <em>TEST</em> Turnover: <em>USDT</em>" \
               f"\n\n<em>For detailed information on how bonuses are calculated, please refer to the " \
               f"'Information' section.</em>"

    await call.message.delete()

    await call.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=inline.back_button(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(structure_handler, text='structure')
