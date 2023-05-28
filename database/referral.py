from database.connection import connect


async def add_first_line(tg_id_id, line_1):
    db, cur = connect()
    all_line_1_tg_id = await get_all_line_1()
    all_line_2_tg_id = await get_all_line_2()
    if tg_id_id in all_line_1_tg_id:
        cur.execute("INSERT INTO app_referral (tg_id_id, line_1) VALUES (%s, %s)", (tg_id_id, line_1,))
        db.commit()
        main_id = await get_id_from_line_1_id(tg_id_id)
        cur.execute("INSERT INTO app_referral (tg_id_id, line_2) VALUES (%s, %s)", (main_id[0], line_1,))
        db.commit()
    if tg_id_id in all_line_2_tg_id:
        main_id = await get_all_ids_from_line_2_id(tg_id_id)
        cur.execute("INSERT INTO app_referral (tg_id_id, line_3) VALUES (%s, %s)", (main_id[0], line_1,))
        db.commit()
    else:
        try:
            cur.execute("INSERT INTO app_referral (tg_id_id, line_1) VALUES (%s, %s)", (tg_id_id, line_1,))
            db.commit()
        except Exception as e:
            print(e)
        finally:
            db.close()
            cur.close()


async def get_all_line_1():
    db, cur = connect()
    try:
        cur.execute("SELECT line_1 FROM app_referral")
        return [tg_id[0] for tg_id in cur.fetchall()]
    finally:
        db.close()
        cur.close()


async def get_all_line_2():
    db, cur = connect()
    try:
        cur.execute("SELECT line_2 FROM app_referral")
        return [tg_id[0] for tg_id in cur.fetchall()]
    finally:
        db.close()
        cur.close()


async def get_id_from_line_1_id(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id_id FROM app_referral WHERE line_1=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


async def get_all_ids_from_line_2_id(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id_id FROM app_referral WHERE line_2=%s", (tg_id,))
        tg_id_id = cur.fetchone()
        cur.execute("SELECT line_1 FROM app_referral WHERE tg_id_id=%s", (tg_id_id[0],))
        line_1 = cur.fetchone()
        return tg_id_id, line_1
    finally:
        db.close()
        cur.close()
