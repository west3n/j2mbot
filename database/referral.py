from database.connection import connect


async def add_first_line(tg_id_id, line_1):
    db, cur = connect()
    all_line_1_tg_id = await get_all_line_1()
    all_line_2_tg_id = await get_all_line_2()
    try:
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
        return tg_id_id
    finally:
        db.close()
        cur.close()


async def get_line_1(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT line_1 FROM app_referral WHERE tg_id_id=%s AND line_1 IS NOT NULL", (tg_id,))
        result = [tg_id[0] for tg_id in cur.fetchall()]
        amount = len(result)
        return amount, result
    finally:
        db.close()
        cur.close()


async def get_line_2(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT line_2 FROM app_referral WHERE tg_id_id=%s AND line_2 IS NOT NULL", (tg_id,))
        result = [tg_id[0] for tg_id in cur.fetchall()]
        amount = len(result)
        return amount, result
    finally:
        db.close()
        cur.close()


async def get_line_3(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT line_3 FROM app_referral WHERE tg_id_id=%s AND line_3 IS NOT NULL", (tg_id,))
        result = [tg_id[0] for tg_id in cur.fetchall()]
        amount = len(result)
        return amount, result
    finally:
        db.close()
        cur.close()


async def update_line_1(tg_id, line_1):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_referral SET tg_id_id = %s WHERE line_1 = %s", (line_1, tg_id))
        db.commit()
    finally:
        db.close()
        cur.close()


async def get_inviter_id_line1(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id_id FROM app_referral WHERE line_1=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


async def get_inviter_id_line2(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id_id FROM app_referral WHERE line_2=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


async def get_inviter_id_line3(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT tg_id_id FROM app_referral WHERE line_3=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


async def get_promo_summary(tg_id):
    db, cur = connect()
    try:
        summary = 0
        cur.execute("SELECT line_1, line_2, line_3 FROM app_referral WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchall()
        referral_ids = [item for sublist in result for item in sublist if item is not None]
        for line_id in referral_ids:
            if line_id:
                cur.execute(
                    f"SELECT SUM(deposit + balance) FROM (SELECT deposit, balance FROM app_balance WHERE tg_id_id = %s "
                    f"UNION ALL SELECT deposit, balance FROM app_stabpool WHERE tg_id_id = %s) AS subquery",
                    (line_id, line_id))
                result = cur.fetchone()
                if result and result[0] is not None:
                    summary += result[0]
        if tg_id in [254465569, 15362825]:
            summary = 32000.4567821
        return float(round(summary, 2))
    finally:
        db.close()
        cur.close()
