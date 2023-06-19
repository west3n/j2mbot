import asyncio

from database.connection import connect


async def status_docs(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT documents_approve FROM app_documents WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


async def add_approve_docs(tg_id):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO app_documents (tg_id_id, documents_approve) VALUES (%s, True)", (tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def check_contract(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT сontract FROM app_documents WHERE tg_id_id=%s", (tg_id,))
        return cur.fetchone()[0]
    finally:
        db.close()
        cur.close()


async def save_contract_path(path, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_documents SET contract = %s WHERE tg_id_id = %s", (path, tg_id))
        db.commit()
    finally:
        db.close()
        cur.close()

