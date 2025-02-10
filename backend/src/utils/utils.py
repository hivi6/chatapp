import time
import sqlite3

from aiohttp import web


async def send_error(ws: web.WebSocketResponse, type: str, msg: str):
    await ws.send_json({"success": False, "type": type, "error": msg})


async def send_data(ws: web.WebSocketResponse, type: str, any):
    await ws.send_json({"success": True, "type": type, "data": any})


def get_user_info(db: sqlite3.Connection, username: str):
    cur = db.execute(
        "SELECT id, username, fullname, password, is_online, last_online, created_at FROM users "
        "WHERE username = ?",
        [username],
    )
    res = cur.fetchall()
    if len(res) == 0:
        return None
    return res[0]


def set_user_status(db: sqlite3.Connection, username: str, is_online: bool) -> str:
    last_online = int(time.time())
    cur = db.cursor()
    cur.execute("BEGIN")
    try:
        cur.execute(
            "UPDATE users SET is_online = ?, last_online = ?  WHERE username = ?",
            [int(is_online), last_online, username],
        )
        cur.execute("COMMIT")
    except sqlite3.Error as e:
        cur.execute("ROLLBACK")
        return "something went wrong: set_user_status"
    return None


def is_contact(db: sqlite3.Connection, user_id: int, contact_id: int):
    cur = db.execute(
        "SELECT COUNT(*) FROM contacts WHERE user_id = ? AND contact_id = ?",
        [user_id, contact_id],
    )
    res = cur.fetchone()
    if res[0] == 0:
        return False
    return True


def add_contact(db: sqlite3.Connection, user_id: int, contact_id: int) -> str:
    cur = db.cursor()
    cur.execute("BEGIN")
    try:
        cur = db.execute(
            "INSERT INTO contacts VALUES (?, ?), (?, ?)",
            [user_id, contact_id, contact_id, user_id],
        )
        cur.execute("COMMIT")
    except sqlite3.Error as e:
        cur.execute("ROLLBACK")
        return "something went wrong: add_contact"
    return None


def get_contacts(db: sqlite3.Connection, user_id: int):
    cur = db.execute(
        "SELECT users.username FROM users, contacts "
        "WHERE users.id = contacts.contact_id AND contacts.user_id = ?",
        [user_id],
    )
    res = cur.fetchall()
    return [t[0] for t in res]
