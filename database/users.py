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
