import asyncio
import datetime

from database.connection import connect


async def get_balance(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit, withdrawal, referral_balance FROM app_balance WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        if result:
            return result
        else:
            cur.execute("INSERT INTO app_balance (tg_id_id, balance, deposit, withdrawal, referral_balance) "
                        "VALUES (%s, 0, 0, 0, 0) RETURNING id", (tg_id,))
            db.commit()
            result = cur.fetchone()[0]
            return 0, 0, 0, result, 0
    finally:
        cur.close()
        db.close()


async def get_balance_status(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_balance WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def get_balance_history(tg_id, transaction):
    db, cur = connect()
    try:
        cur.execute("SELECT date, amount, description FROM app_balancehistory WHERE tg_id_id=%s AND transaction=%s",
                    (tg_id, transaction))
        return cur.fetchall()
    finally:
        cur.close()
        db.close()


async def insert_balance_history(tg_id, amount, hash):
    db, cur = connect()
    try:
        now = datetime.datetime.now()
        cur.execute("INSERT INTO app_balancehistory (tg_id_id, transaction, date, amount, status, description) "
                    "VALUES (%s, %s, %s, %s, %s, %s)", (tg_id, 'IN', now, amount, True, hash))
        db.commit()
    finally:
        cur.close()
        db.close()


async def insert_deposit(tg_id, deposit):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET balance = balance + %s WHERE tg_id_id = %s", (deposit, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_withdrawal_history(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT COUNT (transaction) FROM app_balancehistory WHERE tg_id_id = %s AND transaction = %s",
                    (tg_id, 'OUT',))
        return cur.fetchone()
    finally:
        cur.close()
        db.close()


async def save_withdrawal_amount(amount, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET withdrawal = %s WHERE tg_id_id = %s", (amount, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_my_balance(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance FROM app_balance WHERE tg_id_id = %s", (tg_id,))
        return cur.fetchone()[0]
    finally:
        cur.close()
        db.close()


async def update_hold(hold, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET hold = %s WHERE tg_id_id = %s", (hold, tg_id))
        db.commit()
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


async def get_first_transaction(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_balancehistory WHERE tg_id_id = %s AND transaction = %s", (tg_id, "IN"))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def update_percentage(tg_id, settings):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET settings=%s WHERE tg_id_id=%s", (settings, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def update_document(tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET document=TRUE WHERE tg_id_id=%s", (tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_balance_line(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit FROM app_balance WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def balance_to_deposit_autoreinvest():
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id_id FROM  app_balance WHERE settings is NULL OR settings = 100")
        tg_ids = [user[0] for user in cur.fetchall()]
        for tg_id in tg_ids:
            balance = await get_my_balance(tg_id)
            print(f"{balance} - {tg_id}")
            cur.execute("UPDATE app_balance SET deposit = deposit + %s, balance = %s WHERE tg_id_id = %s", (float(round(balance, 2)), 0.0, tg_id,))
            db.commit()
    finally:
        cur.close()
        db.close()



async def balance_to_deposit_invest():
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id_id FROM  app_balance WHERE settings = 50")
        tg_ids = [user[0] for user in cur.fetchall()]
        for tg_id in tg_ids:
            balance = await get_my_balance(tg_id)
            deposit = int(balance) / 2
            cur.execute("UPDATE app_balance SET deposit = deposit + %s, balance = %s WHERE tg_id_id = %s",
                        (deposit, deposit, tg_id,))
            db.commit()
    finally:
        cur.close()
        db.close()


async def add_weekly_profit(weekly_profit, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET weekly_profit = %s WHERE tg_id_id = %s", (weekly_profit, tg_id, ))
        db.commit()
    finally:
        db.close()
        cur.close()


async def update_weekly_deposit(tg_id, weekly_profit):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET deposit = deposit + %s WHERE tg_id_id = %s", (weekly_profit, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def transfer_deposit_to_balance():
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id_id FROM app_balance")
        tg_ids = [user[0] for user in cur.fetchall()]
        for tg_id in tg_ids:
            cur.execute("SELECT deposit FROM app_balance WHERE tg_id_id = %s", (tg_id, ))
            deposit = cur.fetchone()[0]
            cur.execute("UPDATE app_balance SET balance = balance + %s, deposit = 0 WHERE tg_id_id = %s",
                        (deposit, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def update_referral_profit(tg_id, profit):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET balance = balance + %s, referral_balance = referral_balance + %s "
                    "WHERE tg_id_id = %s",
                    (profit, profit, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_balance_(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit FROM app_balance WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()