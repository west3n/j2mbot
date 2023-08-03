import asyncio
import decouple

from aiogram import Dispatcher, types
from demo import dm_inline, dm_database
from database import users, balance, nft, binance_db


async def balance_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    user_balance = await dm_database.get_demo_balance(call.from_user.id)
    referral = await balance.get_balance(call.from_user.id)
    photo = decouple.config("BANNER_BALANCE")
    dao = await nft.nft_id(call.from_user.id)

    text = f"Ваш индивидуальный номер участника DAO, зафиксированный в смарт-контракте: {dao}" \
           f"\n\n💵 <em>Коллективный аккаунт</em>" \
           f"\n<b>Ваш баланс:</b> {round(user_balance[1], 2)} USDT" \
           f"\n<b>Активный депозит:</b> {round(user_balance[2], 2)} USDT"
    text += f"\n\n💰 <em>Личный аккаунт</em>" \
            f"\n<b>Баланс Binance API:</b> {round(user_balance[5], 2) if user_balance[5] is not None else 0.0}" \
            f"\n<b>Баланс J2M:</b> {round(user_balance[6], 2)}" \
            f"\n<b>Активный депозит:</b> {round(user_balance[7], 2)}"
    text += f"\n\n<b>Сумма зарезервированная на вывод:</b> 0.0 USDT " \
            f"USDT" if int(user_balance[2]) > 0 else ""
    text += "\n\n<a href='https://telegra.ph/Grafik-raboty-bota-vysokochastotnoj-torgovli-07-13'>График работы " \
            "торгового бота</a>"
    if language[4] == "EN":
        text = f"Your individual DAO participant number recorded in the smart contract: {dao}" \
               f"\n\n💵 <em>Collective Account</em>" \
               f"\n<b>Your balance:</b> {round(user_balance[1], 2)} USDT" \
               f"\n<b>Active deposit:</b> {round(user_balance[2], 2)} USDT"
        text += f"\n\n💰 <em>Personal Account</em>" \
                f"\n<b>Binance API balance:</b> {round(user_balance[5], 2)}" \
                f"\n<b>J2M balance:</b> {round(user_balance[6], 2)}" \
                f"\n<b>Active deposit:</b> {round(user_balance[7], 2)}"
        text += f"\n\n<b>Amount reserved for withdrawal:</b> {round(user_balance[2], 2)} USDT" if int(
            user_balance[2]) > 0 else ""
        text += "\n\n<a href='https://telegra.ph/Grafik-raboty-bota-vysokochastotnoj-torgovli-07-13'>" \
                "Trading bot work schedule (RU)</a>"

        photo = decouple.config("BANNER_BALANCE_EN")
    await call.message.delete()
    await call.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=dm_inline.dm_balance_history(language[4]))


async def withdrawal_refill_history(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    history_type = 'OUT' if call.data == 'dm_withdrawal_history' else 'IN'
    if call.data == 'dm_withdrawal_history':
        history_text = 'вывода'
        if language[4] == "EN":
            history_text = 'withdrawal'
    else:
        history_text = 'пополнения'
        if language[4] == 'EN':
            history_text = 'refill'
    all_user_data = await dm_database.get_balance_history(call.from_user.id, history_type)
    for user_data in all_user_data:
        text = f"<b>Дата:</b> {user_data[0].strftime('%d.%m.%Y %H:%M:%S')}\n<b>Cумма:</b> {user_data[1]}" \
               f"\n<b>Хэш транзакции:</b> {user_data[2]}"
        if language[4] == "EN":
            hash_ = user_data[2]
            hash_ = 'Personal Account' if hash_ == 'Личный аккаунт' else hash_
            text = f"<b>Date:</b> {user_data[0].strftime('%d.%m.%Y %H:%M:%S')}\n<b>Amount:</b> {user_data[1]}" \
                   f"\n<b>Transaction Hash:</b> {hash_}"
        await call.message.answer(text)
    if not all_user_data:
        text = f'У вас нет истории {history_text}!'
        if language[4] == "EN":
            text = f'You have no {history_text} history!'
        await call.message.answer(text, reply_markup=dm_inline.dm_back_button(language[4]))
    else:
        text = f'Вывод истории завершён!'
        if language[4] == "EN":
            text = f'History output completed!'
        await call.message.answer(f"{text}", reply_markup=dm_inline.dm_back_button(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(balance_handler, text='dm_balance')
    dp.register_callback_query_handler(withdrawal_refill_history,
                                       lambda c: c.data in ['dm_withdrawal_history', 'dm_refill_history'])
