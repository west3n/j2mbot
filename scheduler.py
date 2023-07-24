import asyncio

import aiogram.utils.exceptions
import decouple

from datetime import datetime, timedelta
from binance.actions import get_balance_j2m
from database import balance, binance_db, users, referral
from aiogram import Bot, types


async def count_users_profit():
    tg_ids = await users.get_all_tg_id()
    now = datetime.now().date() - timedelta(days=1)
    profit_percentage = await binance_db.get_weekly_profit(now)
    for tg_id in tg_ids:
        deposit = await balance.get_balance_status(tg_id)
        weekly_profit = 0
        try:
            deposit_ = deposit[2]
        except TypeError:
            deposit_ = 0
        if deposit_ < 15000:
            if deposit_ == 0:
                pass
            elif deposit_ < 5000:
                weekly_profit = deposit_ * (profit_percentage[0] / 100) * 0.4
            elif deposit_ >= 5000:
                weekly_profit = deposit_ * (profit_percentage[0] / 100) * 0.45
            await balance.add_weekly_profit(weekly_profit, tg_id)
            bot = Bot(token=decouple.config("BOT_TOKEN"))
            session = await bot.get_session()
            line_3 = await referral.get_inviter_id_line3(tg_id)
            line_2 = await referral.get_inviter_id_line2(tg_id)
            line_1 = await referral.get_inviter_id_line1(tg_id)
            try:
                referral_profit_1 = 0
                if line_1[0]:
                    referral_profit_1 = round(weekly_profit * 0.05, 2)
                    await balance.update_referral_profit(line_1[0], referral_profit_1)
            except TypeError:
                referral_profit_1 = 0
            try:
                referral_profit_2 = 0
                if line_2[0]:
                    referral_profit_2 = round(weekly_profit * 0.03, 2)
                    await balance.update_referral_profit(line_2[0], referral_profit_2)
            except TypeError:
                referral_profit_2 = 0
            try:
                referral_profit_3 = 0
                if line_3[0]:
                    referral_profit_3 = round(weekly_profit * 0.02, 2)
                    await balance.update_referral_profit(line_3[0], referral_profit_3)
            except TypeError:
                referral_profit_3 = 0
            try:
                await bot.send_message(
                    chat_id=tg_id,
                    text=f"<b>📨 Отчет на {datetime.now().date().strftime('%d.%m.%Y')}</b>"
                         f"\n\n<em>💰 Ваша доходность за торговую неделю:"
                         f"</em> {round(weekly_profit, 2)} USDT"
                         f"<em>\n\n📈 Общий профит J2M:</em> {round(profit_percentage[0], 2)} %"
                         f"\n\n<em>👨‍👦‍👦 Партнерские начисления:</em>"
                         f"\n   ↳ <em>1 линия (5% от дохода): {referral_profit_1} USDT </em>"
                         f"\n   ↳ <em>2 линия (3% от дохода): {referral_profit_2} USDT </em>"
                         f"\n   ↳ <em>3 линия (2% от дохода): {referral_profit_3} USDT </em>"
                         f"\n\n\n<em>Баланс будет обновлен в течение суток!</em> "
                         f"\n\n<a href='https://telegra.ph/Kak-vyschityvaetsya-dohodnost-polzovatelya-J2M-07-21-2'>"
                         f"Подробнее о правилах начисления доходности</a>",
                    parse_mode=types.ParseMode.HTML)
            except aiogram.utils.exceptions.BotBlocked:
                await bot.send_message(chat_id=decouple.config("GROUP_ID"),
                                       text=f"Пользователь с ID {tg_id} заблокировал бота!")
            await session.close()


async def weekly_deposit_update():
    tg_ids = await users.get_all_tg_id()
    for tg_id in tg_ids:
        try:
            weekly_deposit = await balance.get_balance_status(tg_id)
            if weekly_deposit[8] != 0 and weekly_deposit[4] == 0:
                await balance.update_weekly_deposit(tg_id, round(weekly_deposit[8], 2))
        except TypeError:
            pass


# Баланс J2M
async def scheduler_balance_j2m():
    print(f"Balance J2M start - [{datetime.now()}]")
    while True:
        now = datetime.now()
        user_balance = await get_balance_j2m()
        if now.hour == 11 and now.minute == 6:
            await binance_db.insert_balance_everyday(user_balance[0], user_balance[1])
            print(f"Insert everyday balance at {now.date()}")
        if now.weekday() == 0 and now.hour == 15 and now.minute == 0:
            await binance_db.insert_balance_j2m_monday(user_balance[0], user_balance[1])
            print(f"Insert monday balance at {now.date()}")
        if now.weekday() == 6 and now.hour == 16 and now.minute == 0:
            await binance_db.insert_balance_j2m_sunday(user_balance[0], user_balance[1])
            print(f"Insert sunday balance at {now.date()}")
        await asyncio.sleep(60 - now.second)


# Понедельник
async def balance_to_deposit():
    print(f"Balance to deposit start - [{datetime.now()}]")
    while True:
        now = datetime.now()
        if now.weekday() == 0 and now.hour == 17 and now.minute == 0:
            await weekly_deposit_update()
            print(f"Update deposit with weekly profit for all users at {now.date()}")
        if now.weekday() == 0 and now.hour == 20 and now.minute == 0:
            await balance.balance_to_deposit_autoreinvest()
            print(f"Update balance to deposit on autoreinvest users at {now.date()}")
            await balance.balance_to_deposit_invest()
            print(f"Update balance to deposit on invest users at {now.date()}")
        await asyncio.sleep(60 - now.second)


# Воскресенье
async def deposit_to_balance():
    print(f"Scheduler run at {datetime.now()}")
    while True:
        now = datetime.now()
        if now.weekday() == 6 and now.hour == 18 and now.minute == 0:
            await count_users_profit()
        if now.weekday() == 6 and now.hour == 20 and now.minute == 0:
            await balance.transfer_deposit_to_balance()
        await asyncio.sleep(60 - now.second)


# async def main():
#     loop = asyncio.get_running_loop()
#     tasks = [
#         loop.create_task(scheduler_balance_j2m()),
#         loop.create_task(balance_to_deposit()),
#         loop.create_task(deposit_to_balance())
#     ]
#     await asyncio.gather(*tasks)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
