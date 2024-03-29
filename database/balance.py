import asyncio
import datetime

from database.connection import connect


async def get_balance(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit, withdrawal, referral_balance "
                    "FROM app_balance WHERE tg_id_id=%s", (tg_id,))
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
        cur.execute("SELECT date, amount, description, transaction_type FROM app_balancehistory WHERE tg_id_id=%s AND transaction=%s",
                    (tg_id, transaction))
        return cur.fetchall()
    finally:
        cur.close()
        db.close()


async def count_balance_history_7_days():
    db, cur = connect()
    try:
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        formatted_date = seven_days_ago
        cur.execute("SELECT SUM(amount) FROM app_balancehistory WHERE date >= %s AND transaction = 'IN'", (formatted_date,))
        sum_in = cur.fetchone()[0]
        cur.execute("SELECT SUM(amount) FROM app_balancehistory WHERE date >= %s AND transaction = 'OUT'", (formatted_date,))
        sum_out = cur.fetchone()[0]
        return round(float(sum_in-sum_out), 2)
    finally:
        cur.close()
        db.close()

async def get_stabpool_refill_sum(tg_id):
    db, cur = connect()
    try:
        cur.execute(
            "SELECT SUM(amount) FROM app_balancehistory WHERE tg_id_id=%s AND transaction=%s AND transaction_type = %s",
            (tg_id, "IN", "Стабилизационный пул"))
        result = cur.fetchone()
        try:
            if result[0]:
                return int(result[0])
            else:
                return 0
        except TypeError:
            return 0
    finally:
        cur.close()
        db.close()


async def get_collective_refill_sum(tg_id):
    db, cur = connect()
    try:
        cur.execute(
            "SELECT SUM(amount) FROM app_balancehistory WHERE tg_id_id=%s AND transaction=%s AND transaction_type = %s",
            (tg_id, "IN", "Коллективный аккаунт"))
        result = cur.fetchone()
        try:
            if result[0]:
                return int(result[0])
            else:
                return 0
        except TypeError:
            return 0
    finally:
        cur.close()
        db.close()


async def get_amount(tg_id, transaction_type):
    db, cur = connect()
    try:
        cur.execute("SELECT SUM(amount) FROM app_balancehistory WHERE tg_id_id=%s AND transaction=%s "
                    "AND transaction_type = %s", (tg_id, "IN", transaction_type,))
        refill = cur.fetchone()
        refill = float(refill[0]) if refill[0] else 0
        cur.execute("SELECT SUM(amount) FROM app_balancehistory WHERE tg_id_id=%s AND transaction=%s "
                    "AND transaction_type = %s", (tg_id, "OUT", transaction_type,))
        out = cur.fetchone()
        out = float(out[0]) if out[0] else 0
        return refill, out
    finally:
        cur.close()
        db.close()


async def insert_balance_history(tg_id, amount, hash, transaction_type):
    db, cur = connect()
    try:
        now = datetime.datetime.now()
        cur.execute("INSERT INTO app_balancehistory (tg_id_id, transaction, date, amount, status, description, transaction_type) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)", (tg_id, 'IN', now, amount, True, hash, transaction_type))
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
        cur.execute("UPDATE app_balance SET withdrawal = withdrawal + %s WHERE tg_id_id = %s", (amount, tg_id,))
        db.commit()
        cur.execute("UPDATE app_balance SET balance = balance - %s WHERE tg_id_id = %s",
                    (amount, tg_id,))
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


async def get_first_transaction(tg_id, transaction_type):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_balancehistory WHERE tg_id_id = %s AND transaction = %s "
                    "AND transaction_type = %s", (tg_id, "IN", transaction_type,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def update_percentage(tg_id, settings):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET settings = %s WHERE tg_id_id=%s", (settings, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_percentage(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT settings FROM app_balance WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            return 100
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
        cur.execute("SELECT tg_id_id FROM app_balance WHERE settings is NULL OR settings = 100")
        tg_ids = [user[0] for user in cur.fetchall()]
        for tg_id in tg_ids:
            balance = await get_my_balance(tg_id)
            cur.execute("UPDATE app_balance SET deposit = deposit + %s, "
                        "balance = %s WHERE tg_id_id = %s", (float(round(balance, 2)), 0.0, tg_id,))
            db.commit()
        cur.execute("SELECT tg_id_id FROM app_balance WHERE settings = 0")
        tg_ids = [user[0] for user in cur.fetchall()]
        for tg_id in tg_ids:
            refill, out = await get_amount(tg_id, "Коллективный аккаунт")
            body = refill - out
            balance_, deposit_ = await get_balance_line(tg_id)
            full_balance = float(balance_) + float(deposit_)
            income = full_balance - body
            cur.execute("UPDATE app_balance SET deposit = deposit + %s, "
                        "balance = %s WHERE tg_id_id = %s", (float(round(body, 2)), income, tg_id,))
            db.commit()
        cur.execute("SELECT tg_id_id FROM app_balance WHERE settings = 50")
        tg_ids = [user[0] for user in cur.fetchall()]
        for tg_id in tg_ids:
            refill, out = await get_amount(tg_id, "Коллективный аккаунт")
            body = refill - out
            balance_, deposit_ = await get_balance_line(tg_id)
            full_balance = float(balance_) + float(deposit_)
            income = (full_balance - body)/2
            body = body + income
            cur.execute("UPDATE app_balance SET deposit = deposit + %s, "
                        "balance = %s WHERE tg_id_id = %s", (float(round(body, 2)), income, tg_id,))
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


async def count_pool():
    db, cur = connect()
    try:
        cur.execute("SELECT SUM(deposit) FROM app_balance")
        result = cur.fetchone()[0]
        cur.execute("SELECT SUM(deposit) FROM app_stabpool")
        result = result + cur.fetchone()[0]
        return round(float(result), 2)
    finally:
        cur.close()
        db.close()
