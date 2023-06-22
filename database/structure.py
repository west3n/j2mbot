from database.connection import connect


async def get_user_form(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM app_form WHERE tg_id_id = %s", (tg_id, ))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()


async def save_user_form(name, socials, tg_id):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO app_form (tg_id_id, name, social) VALUES (%s, %s, %s)", (tg_id, name, socials))
        db.commit()
    finally:
        db.close()
        cur.close()


async def update_name(tg_id, name):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_form SET name = %s WHERE tg_id_id = %s", (name, tg_id))
        db.commit()
    finally:
        db.close()
        cur.close()


async def update_socials(tg_id, socials):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_form SET social = %s WHERE tg_id_id = %s", (socials, tg_id))
        db.commit()
    finally:
        db.close()
        cur.close()
