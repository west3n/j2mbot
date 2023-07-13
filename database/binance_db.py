import asyncio
import datetime

from database.connection import connect


async def get_binance_keys(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT api_key, secret_key FROM app_binance WHERE tg_id_id=%s",
                    (tg_id, ))
        return cur.fetchone()
    finally:
        cur.close()
        db.close()


async def save_binance_keys(tg_id, api_key, api_secret):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO app_binance (tg_id_id, api_key, secret_key) VALUES (%s, %s, %s)",
                    (tg_id, api_key, api_secret, ))
        db.commit()
    finally:
        cur.close()
        db.close()


async def check_binance_keys(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_binance WHERE tg_id_id=%s", (tg_id,))
        return cur.fetchone()
    finally:
        cur.close()
        db.close()


async def insert_balance_j2m_monday(balance_usdt, balance_busd):
    db, cur = connect()
    try:
        now = datetime.datetime.now().date()
        cur.execute("INSERT INTO app_balancej2m (date_monday, balance_monday_usdt, balance_monday_busd) "
                    "VALUES (%s, %s, %s)", (now, balance_usdt, balance_busd, ))
        db.commit()
    finally:
        cur.close()
        db.close()


async def insert_balance_j2m_sunday(balance_usdt, balance_busd):
    db, cur = connect()
    try:
        sunday = datetime.datetime.now().date()
        monday = sunday - datetime.timedelta(days=7) #sunday.weekday()
        cur.execute("SELECT balance_monday_usdt, balance_monday_busd FROM app_balancej2m WHERE "
                    "date_monday = %s", (monday, ))
        monday_balance = cur.fetchone()
        total_balance_monday = monday_balance[0] + monday_balance[1]
        total_balance_sunday = balance_usdt + balance_busd
        profit = (((total_balance_sunday - total_balance_monday) / total_balance_monday) * 100)
        cur.execute("UPDATE app_balancej2m SET date_sunday = %s, balance_sunday_usdt = %s, balance_sunday_busd = %s, "
                    "profit = %s WHERE date_monday = %s", (sunday, balance_usdt, balance_busd, round(profit, 2),
                                                           monday, ))
        db.commit()
    finally:
        cur.close()
        db.close()


async def insert_balance_everyday(balance_usdt, balance_busd):
    db, cur = connect()
    try:
        now = datetime.datetime.now().date()
        cur.execute("INSERT INTO app_everydaybalance (date, balance_usdt, balance_busd, total) "
                    "VALUES (%s, %s, %s, %s)", (now, balance_usdt, balance_busd, int(balance_usdt) + int(balance_busd)))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_api_keys():
    db, cur = connect()
    try:
        cur.execute("SELECT api_key, secret_key FROM app_apikeys")
        return cur.fetchall()
    finally:
        cur.close()
        db.close()


async def get_weekly_profit(date):
    db, cur = connect()
    try:
        cur.execute("SELECT profit FROM app_balancej2m WHERE date_sunday = %s", (date,))
        return cur.fetchone()
    finally:
        cur.close()
        db.close()

