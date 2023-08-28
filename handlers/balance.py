import asyncio
import decouple

from aiogram import Dispatcher, types
from keyboards import inline
from database import users, balance, nft, binance_db, stabpool


async def balance_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    user_balance = await balance.get_balance(call.from_user.id)
    photo = decouple.config("BANNER_BALANCE")
    dao = await nft.nft_id(call.from_user.id)
    binance_balance = await binance_db.get_binance_ac(call.from_user.id)
    stabpool_data = await stabpool.get_stabpool_data(call.from_user.id)
    stabpool_balance = round(stabpool_data[0], 2) if stabpool_data else None
    stabpool_deposit = round(stabpool_data[1], 2) if stabpool_data else None
    stabpool_withdrawal = round(stabpool_data[2], 2) if stabpool_data else None
    text = f"Ваш индивидуальный номер участника DAO, зафиксированный в смарт-контракте: {dao}" \
           f"\n\n💵 <em>Коллективный аккаунт</em>" \
           f"\n<b>Ваш баланс:</b> {round(user_balance[0], 2)} USDT" \
           f"\n<b>Активный депозит:</b> {round(user_balance[1], 2)} USDT"
    try:
        text += f"\n\n💰 <em>Личный аккаунт</em>" \
                f"\n<b>Баланс Binance API:</b> {round(binance_balance[0], 2)}" \
                f"\n<b>Баланс J2M:</b> {round(binance_balance[1], 2)}" \
                f"\n<b>Активный депозит:</b> {round(binance_balance[2], 2)}" if binance_balance is not None else ""
    except TypeError:
        pass
    text += f'\n\n<em>Стабилизационный пул</em>' \
            f'\n<b>Баланс:</b> {stabpool_balance} USDT' if stabpool_balance else ''
    text += f'\n<b>Активный депозит:</b> {stabpool_deposit} USDT' if stabpool_deposit else ''
    text += f"\n\n<b>👨‍👦‍👦 Партнерские начисления:</b> {round(user_balance[3], 2)} USDT"
    text += f"\n\n<b>Сумма зарезервированная на вывод (коллективный аккаунт):</b> {round(user_balance[2], 2)} " \
            f"USDT" if int(user_balance[2]) > 0 else ""
    text += f"\n\n<b>Сумма зарезервированная на вывод (стабилизационный пул):</b> {stabpool_withdrawal} " \
            f"USDT" if stabpool_withdrawal else ""
    text += "\n\n<a href='https://telegra.ph/Grafik-raboty-bota-vysokochastotnoj-torgovli-07-13'>График работы " \
            "торгового бота</a>"
    if language[4] == "EN":
        text = f"Your individual participant number in the DAO, recorded in the smart contract: {dao}" \
               f"\n\n💵 <em>Collective Account</em>" \
               f"\n<b>Your Balance:</b> {round(user_balance[0], 2)} USDT" \
               f"\n<b>Active Deposit:</b> {round(user_balance[1], 2)} USDT"
        try:
            text += f"\n\n💰 <em>Personal Account</em>" \
                    f"\n<b>Binance API Balance:</b> {round(binance_balance[0], 2)}" \
                    f"\n<b>J2M Balance:</b> {round(binance_balance[1], 2)}" \
                    f"\n<b>Active Deposit:</b> {round(binance_balance[2], 2)}" if binance_balance is not None else ""
        except TypeError:
            pass
        text += f'\n\n<em>Stabilization Pool</em>' \
                f'\n<b>Balance:</b> {stabpool_balance} USDT' if stabpool_balance else ''
        text += f'\n<b>Active Deposit:</b> {stabpool_deposit} USDT' if stabpool_deposit else ''
        text += f"\n\n<b>👨‍👦‍👦 Partner Earnings:</b> {round(user_balance[3], 2)} USDT"
        text += f"\n\n<b>Amount Reserved for Withdrawal (Collective Account):</b> {round(user_balance[2], 2)} " \
                f"USDT" if int(user_balance[2]) > 0 else ""
        text += f"\n\n<b>Amount Reserved for Withdrawal (Stabilization Pool):</b> {stabpool_withdrawal} " \
                f"USDT" if stabpool_withdrawal else ""
        text += "\n\n<a href='https://telegra.ph/Grafik-raboty-bota-vysokochastotnoj-torgovli-07-13'>Trading Bot Work Schedule</a>"
        photo = decouple.config("BANNER_BALANCE_EN")
    await call.message.delete()
    try:
        if user_balance[4]:
            text_x = await users.get_text("Создание кошелька #1", language[4])
            text_x2 = await users.get_text("Создание кошелька #2", language[4])
            text_x2 = text_x2.replace("{ключ}", f'{user_balance[3]}')
            message = await call.message.answer(text_x)
            await call.bot.send_chat_action(call.message.chat.id, "typing")
            await asyncio.sleep(1)
            await call.bot.delete_message(chat_id=call.message.chat.id,
                                          message_id=message.message_id)
            await call.message.answer(text_x2)
            await call.bot.send_chat_action(call.message.chat.id, "upload_photo")
            await asyncio.sleep(1)
    except IndexError:
        pass
    await call.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=inline.balance_history(language[4]))


async def withdrawal_refill_history(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    await call.message.delete()
    history_type = 'OUT' if call.data == 'withdrawal_history' else 'IN'
    if call.data == 'withdrawal_history':
        history_text = 'вывода'
        if language[4] == "EN":
            history_text = 'withdrawal'
    else:
        history_text = 'пополнения'
        if language[4] == 'EN':
            history_text = 'refill'
    all_user_data = await balance.get_balance_history(call.from_user.id, history_type)
    for user_data in all_user_data:
        text = f"<b>Дата:</b> {user_data[0].strftime('%d.%m.%Y %H:%M:%S')}\n<b>Cумма:</b> {user_data[1]}" \
               f"\n<b>Хэш транзакции:</b> {user_data[2]}" \
               f"\n<b>Тип аккаунта:</b> {user_data[3]}"
        if language[4] == "EN":
            hash_ = user_data[2]
            hash_ = 'Personal Account' if hash_ == 'Личный аккаунт' else hash_
            text = f"<b>Date:</b> {user_data[0].strftime('%d.%m.%Y %H:%M:%S')}" \
                   f"\n<b>Amount:</b> {user_data[1]}" \
                   f"\n<b>Transaction Hash:</b> {hash_}" \
                   f"\n<b>Account type:</b> {user_data[3]}"
        await call.message.answer(text)
    if not all_user_data:
        text = f'У вас нет истории {history_text}!'
        if language[4] == "EN":
            text = f'You have no {history_text} history!'
        await call.message.answer(text, reply_markup=inline.back_button(language[4]))
    else:
        text = f'Вывод истории завершён!'
        if language[4] == "EN":
            text = f'History output completed!'
        await call.message.answer(f"{text}", reply_markup=inline.back_button(language[4]))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(balance_handler, text='balance')
    dp.register_callback_query_handler(withdrawal_refill_history,
                                       lambda c: c.data in ['withdrawal_history', 'refill_history'])
