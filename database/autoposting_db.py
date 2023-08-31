from database.connection import connect


async def get_post_data(post_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM autoposting_autoposting WHERE id = %s", (post_id, ))
        result = cur.fetchone()
        return result
    finally:
        cur.close()
        db.close()


async def approve_post(post_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE autoposting_autoposting SET accept = true WHERE id = %s", (post_id,))
        db.commit()
    finally:
        cur.close()
        db.close()
