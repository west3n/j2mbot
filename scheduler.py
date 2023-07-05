import asyncio
from datetime import datetime
from binance.actions import get_balance_j2m
from database import balance, binance_db


async def scheduler_balance_j2m():
    print(f"Scheduler run at {datetime.now()}")
    while True:
        now = datetime.now()
        user_balance = await get_balance_j2m()
        if now.hour == 10:
            await binance_db.insert_balance_everyday(user_balance)
            print(f"Insert everyday balance at {now.date()}")
        if now.weekday() == 0 and now.hour == 10:
            await binance_db.insert_balance_j2m_monday(user_balance)
            print(f"Insert monday balance at {now.date()}")
        if now.weekday() == 6 and now.hour == 10:
            await binance_db.insert_balance_j2m_sunday(user_balance)
            print(f"Insert sunday balance at {now.date()}")
        await asyncio.sleep(60 - now.second)


async def balance_to_deposit():
    print(f"Scheduler run at {datetime.now()}")
    while True:
        now = datetime.now()
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
