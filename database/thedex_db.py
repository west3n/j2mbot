import datetime

from database.connection import connect


async def insert_transaction(tg_id, amount, invoiceId):
    now = datetime.datetime.now()
    db, cur = connect()
    try:
        cur.execute("INSERT INTO app_thedex (tg_id_id, amount, \"invoiceId\", date) VALUES (%s, %s, %s, %s)",
                    (tg_id, amount, invoiceId, now,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def get_transaction(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_thedex WHERE (status IS NULL OR status='') AND tg_id_id = %s", (tg_id,))
        rows = cur.fetchall()
        return rows
    finally:
        db.close()
        cur.close()


async def insert_status(tg_id, invoice_id, status):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_thedex SET status=%s WHERE tg_id_id=%s AND \"invoiceId\"=%s", (status, tg_id, invoice_id,))
        db.commit()
    finally:
        db.close()
        cur.close()

