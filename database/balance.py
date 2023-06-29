import datetime

from database.connection import connect


async def get_balance(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit, withdrawal FROM app_balance WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        if result:
            return result
        else:
            cur.execute("INSERT INTO app_balance (tg_id_id, balance, deposit, withdrawal) "
                        "VALUES (%s, 0, 0, 0) RETURNING id", (tg_id,))
            db.commit()
            result = cur.fetchone()[0]
            return 0, 0, 0, result
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


async def get_document_status(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT document FROM app_balance WHERE tg_id_id=%s", (tg_id,))
        return cur.fetchone()
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
