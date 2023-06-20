import asyncio

from database.connection import connect


async def user_data(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_j2muser WHERE tg_id=%s", (tg_id,))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()


async def add_new_user(tg_id, tg_username, tg_name, lang):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO app_j2muser (tg_id, tg_username, tg_name, language) "
                    "VALUES (%s, %s, %s, %s)", (tg_id, tg_username, tg_name, lang,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def update_user_language(tg_id, lang):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_j2muser SET language = %s WHERE tg_id = %s", (lang, tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def get_tg_username(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT tg_username FROM app_j2muser WHERE tg_id=%s", (tg_id,))
        result = cur.fetchone()
        if result[0]:
            return result[0]
        else:
            cur.execute("SELECT tg_name FROM app_j2muser WHERE tg_id=%s", (tg_id,))
            result = cur.fetchone()
            return result[0]
    finally:
        db.close()
        cur.close()


async def get_tg_full_name(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT tg_name FROM app_j2muser WHERE tg_id=%s", (tg_id,))
        result = cur.fetchone()
        return result[0]
    finally:
        db.close()
        cur.close()


async def get_all_tg_id():
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id FROM app_j2muser")
        return [tg_id[0] for tg_id in cur.fetchall()]
    finally:
        db.close()
        cur.close()


async def insert_alias(alias, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_j2muser SET alias = %s WHERE tg_id = %s", (alias, tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def save_wallet(wallet, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_j2muser SET wallet = %s WHERE tg_id = %s", (wallet, tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def set_status(status, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_j2muser SET status = %s WHERE tg_id = %s", (status, tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def check_status(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT status FROM app_j2muser WHERE tg_id = %s", (tg_id,))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()