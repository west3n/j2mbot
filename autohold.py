import asyncio
import datetime

import aiogram.utils.exceptions
from aiogram import Bot
from decouple import config

from database.connection import connect

async def get_balance(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit FROM app_balance WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()

async def get_language(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT language FROM app_j2muser WHERE tg_id=%s", (tg_id,))
        result = cur.fetchone()
        return result[0]
    finally:
        db.close()


async def get_first_transaction(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_balancehistory WHERE tg_id_id = %s AND transaction = %s", (tg_id, "IN"))
        result = cur.fetchone()
        print(result)
        return result
    finally:
        cur.close()
        db.close()


async def get_tg_id_all():
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id FROM app_j2muser")
        result = cur.fetchall()
        if result:
            return [tg_id[0] for tg_id in result]
        else:
            return None
    finally:
        cur.close()
        db.close()



async def get_hold(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT hold FROM app_balance WHERE tg_id_id = %s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def update_hold_collective(tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET hold = hold + 30 WHERE tg_id_id = %s", (tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def autohold_collective():
    tg_ids = await get_tg_id_all()
    new_list = []
    for tg_id in tg_ids:
        first_trans = await get_first_transaction(tg_id)
        date_first = first_trans[2] if first_trans is not None else None
        hold = await get_hold(tg_id)
        hold = hold[0] if hold is not None else 0
        withdrawal_date = date_first + datetime.timedelta(days=hold) if date_first and hold else None
        now = datetime.datetime.now()
        now = now.replace(tzinfo=datetime.timezone.utc)
        if withdrawal_date:
            if now >= date_first + datetime.timedelta(days=hold):
                balance, deposite = await get_balance(tg_id)
                if float(first_trans) >= (float(balance) + float(deposite)):
                    new_list.append(tg_id)
    tg_ids = new_list
    for tg_id in tg_ids:
        hold = await get_hold(tg_id)
        hold = hold[0] if hold is not None else 0
        await update_hold_collective(tg_id)
        first_trans = await get_first_transaction(tg_id)
        date_first = first_trans[2]
        withdrawal_date = date_first + datetime.timedelta(days=(hold + 30))
        withdrawal_date = withdrawal_date.strftime("%d.%m.%Y")
        bot = Bot(config("BOT_TOKEN"))
        session = await bot.get_session()
        language = await get_language(tg_id)
        text = "[Коллективный аккаунт] Ваш холд автоматически продлен.\n\n" \
               f"Новая дата окончания холда: {withdrawal_date}"
        if language == "EN":
            text = "Your hold has been automatically extended!\n\n" \
               f"New hold end date: {withdrawal_date}"
        try:
            await bot.send_message(tg_id, text)
            await session.close()
        except aiogram.utils.exceptions.BotBlocked:
            await session.close()

# async def main():
#     while True:
#         now = datetime.datetime.now()
#         if now.weekday() == 2 and now.hour == 8 and now.minute == 0:
#             await autohold_collective()
#             break
#         else:
#             next_minute = (now + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
#             seconds_until_next_minute = (next_minute - now).total_seconds()
#             await asyncio.sleep(seconds_until_next_minute)
#
# if __name__ == "__main__":
#     asyncio.run(main())
