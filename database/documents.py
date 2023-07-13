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


# async def add_approve_docs(tg_id):
#     db, cur = connect()
#     try:
#         cur.execute(
#             "INSERT INTO app_documents (tg_id_id, documents_approve, approve_contract) VALUES (%s, TRUE, FALSE)",
#             (tg_id,))
#         db.commit()
#     finally:
#         db.close()
#         cur.close()


async def check_approve_contract(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT approve_contract FROM app_documents WHERE tg_id_id=%s", (tg_id,))
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


async def insert_it_product(tg_id):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO app_documents (tg_id_id, documents_approve, approve_contract, it_product) "
                    "VALUES (%s, FALSE, FALSE, TRUE)", (tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def update_kyc(tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE app_documents SET documents_approve=TRUE WHERE tg_id_id=%s", (tg_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def check_it_product(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT it_product FROM app_documents WHERE tg_id_id=%s", (tg_id,))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()


async def check_kyc(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT documents_approve FROM app_documents WHERE tg_id_id=%s", (tg_id,))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()
