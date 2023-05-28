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
