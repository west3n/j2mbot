import datetime

from database.connection import connect


async def insert_new_output(tg_id, amount, wallet):
    db, cur = connect()
    now = datetime.datetime.now()
    try:
        cur.execute("INSERT INTO app_output (tg_id_id, amount, date, wallet, approve) VALUES (%s, %s, %s, %s, %s)",
                    (tg_id, amount, now, wallet, False))
        db.commit()
    finally:
        db.close()
        cur.close()

