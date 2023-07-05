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


async def insert_balance_j2m_monday(balance):
    db, cur = connect()
    try:
        now = datetime.datetime.now().date()
        cur.execute("INSERT INTO app_balancej2m (date_monday, balance_monday) VALUES (%s, %s)", (now, balance,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def insert_balance_j2m_sunday(balance):
    db, cur = connect()
    try:
        sunday = datetime.datetime.now().date()
        monday = sunday - datetime.timedelta(days=sunday.weekday())
        cur.execute("SELECT balance_monday FROM app_balancej2m WHERE date_monday = %s", (monday, ))
        monday_balance = cur.fetchone()
        profit = (((balance - monday_balance[0]) / monday_balance[0]) * 100)
        cur.execute("UPDATE app_balancej2m SET date_sunday = %s, balance_sunday = %s, profit = %s "
                    "WHERE date_monday = %s", (sunday, balance, round(profit, 2), monday, ))
        db.commit()
    finally:
        cur.close()
        db.close()


async def insert_balance_everyday(balance):
    db, cur = connect()
    try:
        now = datetime.datetime.now().date()
        cur.execute("INSERT INTO app_everydaybalance (date, balance) VALUES (%s, %s)", (now, balance,))
        db.commit()
    finally:
        cur.close()
        db.close()
