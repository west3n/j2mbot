import asyncio

import decouple
from aiogram import Dispatcher, types
from keyboards import inline
from database import users, balance


async def balance_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    user_balance = await balance.get_balance(call.from_user.id)
    photo = decouple.config("BANNER_BALANCE")
    balance_id = await balance.get_balance_status(call.from_user.id)
    text = f"<b>Ваш индивидуальный номер участника DAO, зафиксированный в смарт-контракте:</b> {balance_id[0]}" \
           f"\n<b>Ваш баланс:</b> {user_balance[0]} USDT\n<b>Активный депозит:</b> {user_balance[1]} USDT" \
           f"\n<b>Партнерские начисления:</b> 0 USDT"
    text += f"\n<b>Сумма зарезервированная на вывод:</b> {user_balance[2]} USDT" if int(user_balance[2]) > 0 else ""
    text += f"\n\nВ данном меню расположены инструменты управления Вашим балансом" \
            f"\n\nГрафик работы бота высокочастотной торговли:" \
            f"\nВключение бота происходит в 18.00 МСК по понедельникам." \
            f"\nВсе участники разместившие свои криптоактивы до 17.30 МСК попадают в сессию, участники " \
            f"разместившие средства после 17.30 МСК попадают на начало сессии на следующей недели." \
            f"\nВыключение и подведение итогов работы за неделю происходит каждое воскресенье во временном " \
            f"промежутке с 17.00 до 22.00 МСК." \
            f"\nАлгоритм рассчитывает прибыль и распределяет между участниками ДАО в воскресенье в 23:00 МСК. " \
            f"После этого участники получают сообщение о начислениях и видят изменения в статистике своих балансов."
    if language[4] == "EN":
        text = f"<b>Your individual DAO participant number, recorded in the smart contract:</b> {balance_id[0]}" \
               f"\n<b>Your balance:</b> {user_balance[0]} USDT\n<b>Active deposit:</b> {user_balance[1]} USDT" \
               f"<b>Partnership earnings:</b> 0 USDT"
        text += f"\n<b>Reserved amount for withdrawal:</b> {user_balance[2]} USDT" if int(user_balance[2]) > 0 else ""
        text += "\n\nIn this menu, you will find tools to manage your balance." \
                "\n\nHigh-frequency trading bot schedule:" \
                "\nThe bot is activated at 18:00 MSK (Moscow Standard Time) on Mondays." \
                "\nParticipants who deposit their crypto assets before 17:30 MSK are included in the current session." \
                "\nParticipants who deposit funds after 17:30 MSK are included in the session starting " \
                "the following week." \
                "\nThe bot is turned off, and weekly performance results are finalized every Sunday " \
                "between 17:00 and 22:00 MSK." \
                "\nThe algorithm calculates profits and distributes them among DAO participants at " \
                "23:00 MSK on Sunday." \
                "Participants receive notifications about their earnings and can see changes in " \
                "their balance statistics."
        photo = decouple.config("BANNER_BALANCE_EN")
    await call.message.delete()
    try:
        if user_balance[3]:
            text_x = f"Ожидайте, бот создает ваш кошелек..."
            text_x2 = f"Ваш кошелек успешно создан!\n\n" \
                      f"<b>Важно! Сохраните это сообщение в виде скриншота или запишите в заметки.</b>\n" \
                      f"Ваш секретный ключ: <b>{user_balance[3]}</b>" \
                      f"\n\n<em>Рекомендуется удалить данное сообщение после сохранения секретного ключа.</em>"
            if language[4] == "EN":
                text_x = f"Expect the bot to create your wallet..."
                text_x2 = f"Your wallet has been successfully created!\n\n" \
                          f"<b>Important! Save this message as a screenshot or note it down.</b>\n" \
                          f"Your secret key: <b>{user_balance[3]}</b>" \
                          f"\n\n<em>It is recommended to delete this message after saving the private key.</em>"
            message = await call.message.answer(text_x)
            await call.bot.send_chat_action(call.message.chat.id, "typing")
            await asyncio.sleep(3)

            await call.bot.delete_message(chat_id=call.message.chat.id,
                                          message_id=message.message_id)
            await call.message.answer(text_x2)
            await call.bot.send_chat_action(call.message.chat.id, "upload_photo")
            await asyncio.sleep(2)
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
    history_text = 'withdrawal' if call.data == 'withdrawal_history' else 'refill'
    all_user_data = await balance.get_balance_history(call.from_user.id, history_type)
    for user_data in all_user_data:
        text = f"<b>Дата:</b> {str(user_data[0]).split('+')[0]}\n<b>Cумма:</b> {user_data[1]}" \
               f"\n<b>Комментарий:</b> {user_data[2]}"
        if language[4] == "EN":
            text = f"<b>Date:</b> {str(user_data[0]).split('+')[0]}\n<b>Amount:</b> {user_data[1]}" \
                   f"\n<b>Comment:</b> {user_data[2]}"
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
