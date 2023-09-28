from database.connection import connect


async def add_new_promo(tg_id, summary, percentage, deposit):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO promo_promo (tg_id_id, structure, percentage, status, deposit, balance, profit) "
                    "VALUES (%s, %s, %s, false, %s, 0, 0) RETURNING id", (tg_id, summary, percentage, deposit,))
        result = cur.fetchone()
        db.commit()
        return result
    finally:
        db.close()
        cur.close()


async def promo_status(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT balance, deposit, structure, percentage, date_start, date_end"
                    "FROM promo_promo WHERE tg_id_id = %s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


async def reduce_media_balance(tg_id, balance):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_balance SET balance = balance + %s WHERE tg_id_id = %s", (balance, tg_id,))
        cur.execute("UPDATE promo_promo SET balance = balance - %s WHERE tg_id_id = %s", (balance, tg_id,))
        db.commit()
    finally:
        cur.close()
        db.close()
