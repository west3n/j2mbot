import datetime

from database.connection import connect


async def insert_demo_mode(tg_id):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO demo_demouser (tg_id_id, balance_collective, deposit_collective, "
                    "balance_personal, deposit_personal) VALUES (%s, 0.0, 0.0, 0.0, 0.0)", (tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def insert_demo_collective_balance(tg_id, deposit):
    db, cur = connect()
    try:
        cur.execute("UPDATE demo_demouser SET balance_collective = balance_collective + %s WHERE tg_id_id = %s",
                    (deposit, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def update_demo_personal_balance(tg_id, amount, binance):
    db, cur = connect()
    try:
        cur.execute("UPDATE demo_demouser SET api_key='ДЕМО', secret_key='ДЕМО',"
                    " balance_binance = %s, balance_personal = balance_personal + %s, "
                    "deposit_personal = deposit_personal WHERE tg_id_id = %s",
                    (binance, amount, tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def get_demo_balance(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM demo_demouser WHERE tg_id_id=%s", (tg_id,))
        # [0]tg_id, [1]balance_collective, [2]deposit_collective,
        # [3]api_key, [4]secret_key, [5]balance_binance,
        # [6]balance_personal, [7]deposit_personal
        return cur.fetchone()
    finally:
        db.close()
        cur.close()


async def get_demo_balance_history(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM demo_demobalancehistory WHERE tg_id_id = %s", (tg_id,))
        return cur.fetchone()
        # [0]tg_id, [1]transaction, [2]date, [3]amount, [4] description, [5]status
    finally:
        db.close()
        cur.close()


async def insert_demo_balance_history(tg_id, amount, trans, descrip):
    db, cur = connect()
    try:
        now = datetime.datetime.now()
        cur.execute("INSERT INTO demo_demobalancehistory (tg_id_id, transaction, date,"
                    " amount, description, status) "
                    "VALUES (%s, %s, %s, %s, %s, %s)", (tg_id, trans, now, amount, descrip, True))
        db.commit()
    finally:
        db.close()
        cur.close()


async def get_balance_history(tg_id, transaction):
    db, cur = connect()
    try:
        cur.execute("SELECT date, amount, description, transaction_type "
                    "FROM demo_demobalancehistory WHERE tg_id_id=%s AND transaction=%s",
                    (tg_id, transaction))
        return cur.fetchall()
    finally:
        cur.close()
        db.close()


async def get_balance(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit, withdrawal "
                    "FROM demo_demostabpool WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        if result:
            return result
        else:
            cur.execute("INSERT INTO demo_demostabpool (tg_id_id, balance, deposit, withdrawal) "
                        "VALUES (%s, 0, 0, 0)", (tg_id,))
            db.commit()
    finally:
        cur.close()
        db.close()


async def get_stabpool_data(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit, withdrawal "
                    "FROM demo_demostabpool WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        if result:
            return result
    finally:
        cur.close()
        db.close()


async def insert_deposit(tg_id, deposit):
    db, cur = connect()
    try:
        cur.execute("UPDATE demo_demostabpool SET balance = balance + %s WHERE tg_id_id = %s", (deposit, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_hold(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT hold FROM demo_demostabpool WHERE tg_id_id = %s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def update_hold(hold, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE demo_demostabpool SET hold = %s WHERE tg_id_id = %s", (hold, tg_id))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_balance_line(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit FROM demo_demostabpool WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def get_balance_status(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM demo_demostabpool WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


