import datetime

from database.connection import connect


async def check_nft_status(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_nft WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


async def check_nft_count():
    db, cur = connect()
    try:
        cur.execute("SELECT COUNT(*) FROM app_nft WHERE address NOTNULL ")
        result = cur.fetchone()[0]
        return result
    finally:
        db.close()
        cur.close()


async def check_nft_count_last_7_days():
    db, cur = connect()
    try:
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        formatted_date = seven_days_ago
        cur.execute("SELECT COUNT(*) FROM app_nft WHERE address NOTNULL AND date >= %s", (formatted_date,))
        result = cur.fetchone()[0]
        return result
    finally:
        db.close()
        cur.close()

async def create_nft(tg_id, invoiceId):
    db, cur = connect()
    try:
        now = datetime.datetime.now()
        cur.execute("INSERT INTO app_nft (tg_id_id, \"invoiceId\", date) VALUES (%s, %s, %s)", (tg_id, invoiceId, now))
        db.commit()
    finally:
        db.close()
        cur.close()


async def delete_error(tg_id):
    db, cur = connect()
    try:
        cur.execute("DELETE FROM app_nft WHERE tg_id_id = %s", (tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def update_nft(tg_id, address, private_key, status):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_nft SET status = %s, address = %s, private_key = %s WHERE tg_id_id = %s RETURNING id",
                    (status, address, private_key, tg_id))
        db.commit()
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


async def nft_id(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT id FROM app_nft WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()[0]
        return result
    finally:
        db.close()
        cur.close()


async def get_ad_status(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT status FROM app_nft WHERE tg_id_id=%s", (tg_id,))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()