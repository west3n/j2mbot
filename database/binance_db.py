from database.connection import connect


async def get_binance_keys(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT api_key, secret_key FROM app_binance WHERE tg_id_id=%s",
                    (tg_id, ))
        return cur.fetchone()
    finally:
        cur.close()
        db.close()


async def save_binance_keys(tg_id, api_key, api_secret):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO app_binance (tg_id_id, api_key, secret_key) VALUES (%s, %s, %s)",
                    (tg_id, api_key, api_secret, ))
        db.commit()
    finally:
        cur.close()
        db.close()


async def check_binance_keys(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_binance WHERE tg_id_id=%s", (tg_id,))
        return cur.fetchone()
    finally:
        cur.close()
        db.close()
