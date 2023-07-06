import asyncio
from datetime import datetime
from binance.actions import get_balance_j2m
from database import balance, binance_db, users


async def count_users_profit():
    tg_ids = await users.get_all_tg_id()
    now = datetime.now().date()
    for tg_id in tg_ids:
        deposit = await balance.get_balance_status(tg_id)
        profit_percentage = await binance_db.get_weekly_profit(now)
        weekly_profit = 0
        if deposit[2] == 0:
            pass
        if deposit[2] < 5000:
            weekly_profit = deposit[2] * (profit_percentage / 100) * 0.4
        if deposit[2] >= 5000:
            weekly_profit = deposit[2] * (profit_percentage / 100) * 0.45
        await balance.add_weekly_profit(weekly_profit, tg_id)


async def weekly_deposit_update():
    tg_ids = await users.get_all_tg_id()
    for tg_id in tg_ids:
        weekly_deposit = await balance.get_balance_status(tg_id)
        if weekly_deposit[9] != 0 and weekly_deposit[4] == 0:
            await balance.update_weekly_deposit(tg_id, weekly_deposit[9])


async def scheduler_balance_j2m():
    print(f"Scheduler run at {datetime.now()}")
    while True:
        now = datetime.now()
        user_balance = await get_balance_j2m()
        if now.hour == 10 and now.minute == 0:
            await binance_db.insert_balance_everyday(user_balance[0], user_balance[1])
            print(f"Insert everyday balance at {now.date()}")
        if now.weekday() == 0 and now.hour == 15 and now.minute == 0:
            await binance_db.insert_balance_j2m_monday(user_balance[0], user_balance[1])
            print(f"Insert monday balance at {now.date()}")
        if now.weekday() == 6 and now.hour == 16 and now.minute == 0:
            await binance_db.insert_balance_j2m_sunday(user_balance[0], user_balance[1])
            print(f"Insert sunday balance at {now.date()}")
        await asyncio.sleep(60 - now.second)



async def balance_to_deposit():
    print(f"Scheduler run at {datetime.now()}")
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



# async def deposit_to_balance():
#     print(f"Scheduler run at {datetime.now()}")
#     while True:
#         now = datetime.now()
#         print(now.weekday())
#         if now.weekday() == 6 and now.hour == 17 and now.minute == 0:
#             await third_notifications.result_notification()
#         next_sunday = now + timedelta(days=(6 - now.weekday()) % 7)
#         next_sunday_17 = next_sunday.replace(hour=17, minute=0, second=0, microsecond=0)
#         time_until_next_sunday = (next_sunday_17 - now).total_seconds()
#         await asyncio.sleep(time_until_next_sunday)


if __name__ == '__main__':
    asyncio.run(scheduler_balance_j2m())
