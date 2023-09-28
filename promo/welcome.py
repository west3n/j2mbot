import asyncio

import decouple
import psycopg2

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import referral, promo_db, users, balance
from handlers import commands, google
from keyboards import inline


def calculate_percentage(value):
    if 30000 <= value < 40000:
        return 10.0
    elif value >= 40000:
        steps = (value - 30000) // 10000
        return max(5.0, 10.0 - (steps * 0.1))
    else:
        return 0.0


class Transfer(StatesGroup):
    amount = State()
    code = State()


async def promo_welcome(msg: types.Message):
    status = await promo_db.promo_status(msg.from_id)
    # 0:balance, 1:deposit, 2:structure, 3:percentage, 4:date_start, 5:date_end, 6:withdrawal
    if status:
        await msg.answer(f"<b>Медиа-программа DAO J2M!</b>"
                         f"\n\nМедиа-баланс (баланс, доступный к переводу): {float(round(status[0], 2))} USDT"
                         f"\nМедиа-депозит: {float(round(status[1], 2))} USDT"
                         f"\nПривлечённый объём капитала: {float(round(status[2], 2))} USDT"
                         f"\nБонус от привлеченного капитала начисляемый медиа партнёру: {status[3]} %"
                         f'\n<em>Вывод медиа-депозита недоступен!</em>'
                         f"\n\n<b>Продолжительность программы:</b>"
                         f"\n<em>Дата старта индивидуальной программы: {status[4].strftime('%d.%m.%Y')}"
                         f"\nДата окончания индивидуальной программы: {status[5].strftime('%d.%m.%Y')}</em>",
                         reply_markup=inline.media_program())
    else:
        summary = await referral.get_promo_summary(msg.from_id)
        percentage = calculate_percentage(summary)
        deposit = round(summary * (float(percentage) / 100), 2)
        user_name = '@' + msg.from_user.username if msg.from_user.username else msg.from_user.full_name
        if summary >= 30000:
            try:
                order = await promo_db.add_new_promo(msg.from_id, summary, percentage, deposit)
                await msg.bot.send_message(chat_id=decouple.config('GROUP_ID'),
                                           text=f"Пользователь {user_name} попытался подключиться к медиа-программе!"
                                                f"\nЗаявка на подключение к программе проходит по условиям, "
                                                f"сумма оборота: {summary} USDT, процент от структуры {percentage}%"
                                                f"\nПожалуйста одобрите заявку в админ-панели: вставить ссылку")
                await msg.answer(
                    f"Заявка #{order[0]} на подключение к медиа-программе передана на рассмотрение администратору!"
                    f"\nПожалуйста, ожидайте ответа.")
            except psycopg2.Error:
                await msg.answer("У вас уже есть заявка на рассмотрении! "
                                 "\nПожалуйста, ожидайте ответа администратора или напишите в Поддержку!")
        else:
            await msg.answer(
                f"Для участия в Медиа-программе сумма активов ваших рефералов должна быть не меньше 30000 USDT."
                f"\nНа данный момент сумма составляет {summary} USDT")
            await msg.bot.send_message(chat_id=decouple.config('GROUP_ID'),
                                       text=f"Пользователь {user_name} попытался подключиться к медиа-программе!"
                                            f"Заявка отклонена, так как сумма оборота пользователя - {summary} USDT")


async def transfer_to_collective(call: types.CallbackQuery):
    status = await promo_db.promo_status(call.from_user.id)
    if status[0] > 0:
        await call.message.edit_text(f"Сумма доступная к переводу: {status[0]}\n\n"
                                     f"Введите сумму перевода:")
        await Transfer.amount.set()
    else:
        await call.answer(show_alert=True, text=f"Сумма доступная к переводу: {status[0]}")


async def transfer_to_collective_step2(msg: types.Message, state: FSMContext):
    status = await promo_db.promo_status(msg.from_user.id)
    if msg.text.isdigit():
        if int(msg.text) <= status[0]:
            code = commands.generate_random_code()
            email = await users.check_email(msg.from_user.id)
            parts = email[0].split('@')
            username = parts[0]
            domain = parts[1]
            masked_username = username[:3] + '*' * (len(username) - 3)
            masked_email = masked_username + '@' + domain
            await google.send_email_message(
                to=email[0],
                subject="DAO J2M transfer",
                message_text=f"Вы заказываете перевод средств {msg.text} USDT "
                             f"на коллективный аккаунт! "
                             f"Для подтверждения создания заявки отправьте боту этот код: {code} "
                             f"\n\nЕсли у вас возникли сложности, или вам нужна помощь, "
                             f"вы можете связаться с нами по этой электронной почте ответным письмом, "
                             f"или напишите нам в телеграм: https://t.me/J2M_Support")
            await state.update_data({"code": code, "amount": int(msg.text)})
            await msg.answer(f"На вашу почту {masked_email} отправлено сообщение с кодом! "
                             f"Введите код для продолжения транзакции:")
            await Transfer.next()
        else:
            await msg.answer(text=f"Сумма доступная к переводу: {status[0]}")
    else:
        await msg.answer("Введите сумму без запятых, точек, букв и прочего!")


async def transfer_to_collective_step3(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if msg.text == data.get("code"):
            amount = data.get("amount")
            await promo_db.reduce_media_balance(msg.from_id, amount)
            await balance.insert_balance_history(msg.from_id, amount, 'transfer', 'Трансфер')
            await google.add_new_transfer_data(msg.from_id, amount)
            await msg.answer(f"Трансфер {amount} USDT с медиа-программы в коллективный аккаунт успешно выполненен!")
            await state.finish()
            await promo_welcome(msg)
        else:
            msg_id = await msg.answer("Трансфер отменен, так как код на почту отличается от введеного. Попробуйте еще раз!")
            await asyncio.sleep(2)
            await msg.bot.delete_message(msg.from_id, msg_id.message_id)
            await state.finish()
            await promo_welcome(msg)


def register(dp: Dispatcher):
    dp.register_message_handler(promo_welcome, commands='j2m_media')
    dp.register_message_handler(transfer_to_collective_step2, state=Transfer.amount)
    dp.register_message_handler(transfer_to_collective_step3, state=Transfer.code)
    dp.register_callback_query_handler(transfer_to_collective, text='media_transfer')

