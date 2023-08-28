from database.connection import connect


async def get_balance(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit, withdrawal "
                    "FROM app_stabpool WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        if result:
            return result
        else:
            cur.execute("INSERT INTO app_stabpool (tg_id_id, balance, deposit, withdrawal) "
                        "VALUES (%s, 0, 0, 0)", (tg_id,))
            db.commit()
    finally:
        cur.close()
        db.close()


async def get_stabpool_data(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit, withdrawal "
                    "FROM app_stabpool WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        if result:
            return result
    finally:
        cur.close()
        db.close()


async def insert_deposit(tg_id, deposit):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_stabpool SET balance = balance + %s WHERE tg_id_id = %s", (deposit, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_hold(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT hold FROM app_stabpool WHERE tg_id_id = %s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def update_hold(hold, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_stabpool SET hold = %s WHERE tg_id_id = %s", (hold, tg_id))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_balance_line(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit FROM app_stabpool WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def get_balance_status(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_stabpool WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def add_weekly_profit(weekly_profit, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_stabpool SET weekly_profit = %s WHERE tg_id_id = %s", (weekly_profit, tg_id, ))
        db.commit()
    finally:
        db.close()
        cur.close()


async def update_weekly_deposit(tg_id, weekly_profit):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_stabpool SET deposit = deposit + %s WHERE tg_id_id = %s", (weekly_profit, tg_id,))
        db.commit()
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
