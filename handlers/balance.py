import asyncio

import decouple
from aiogram import Dispatcher, types
from keyboards import inline
from database import users, balance


async def balance_handler(call: types.CallbackQuery):
    language = await users.user_data(call.from_user.id)
    user_balance = await balance.get_balance(call.from_user.id)
    print(user_balance)
    photo = decouple.config("BANNER_BALANCE")

    text = f"<b>Ваш баланс:</b> {user_balance[0]} USDT\n<b>Активный депозит:</b> {user_balance[1]} USDT"
    text += f"\n<b>Сумма зарезервированная на вывод:</b> {user_balance[2]} USDT" if int(user_balance[2]) > 0 else ""
    text += "\n\nНачисление процентов происходит на активный депозит каждый день в промежутке от " \
            f"<b>22.00 до 24.00</b> московского времени. Мы начисляем процент от дневной доходности активного " \
            f"депозита. Подробнее об условиях распределения процентов вы сможете узнать кликнув по кнопке " \
            f"“Информация”."
    if language[4] == "EN":
        text = f"<b>Your balance:</b> {user_balance[0]} USDT\n<b>Active deposit:</b> {user_balance[1]} USDT"
        text += f"\n<b>Reserved amount for withdrawal:</b> {user_balance[2]} USDT" if int(user_balance[2]) > 0 else ""
        text += f"\n\nInterest accrual occurs on the active deposit every day within the period from " \
                f"<b>22:00 to 24:00</b> Moscow time. We calculate interest based on the daily earnings " \
                f"of the active deposit. For more information on interest distribution terms, you can click on the " \
                f"“Information” button."
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
