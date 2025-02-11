import time
import sqlite3

from aiohttp import web


async def send_error(ws: web.WebSocketResponse, type: str, msg: str):
    await ws.send_json({"success": False, "type": type, "error": msg})


async def send_data(ws: web.WebSocketResponse, type: str, any):
    await ws.send_json({"success": True, "type": type, "data": any})


async def send_data_convo(
    convo_id: int,
    wss: dict[str, web.WebSocketResponse],
    db: sqlite3.Connection,
    type: str,
    any,
):
    cur = db.execute(
        "SELECT users.username FROM members, users WHERE "
        "members.user_id = users.id AND members.conversation_id = ?",
        [convo_id],
    )
    for res in cur.fetchall():
        username = res[0]
        ws = wss.get(username, None)
        if ws is None:  # Check if websocket exists
            continue
        await send_data(ws, type, any)


async def send_data_contact(
    wss: dict[str, web.WebSocketResponse],
    username: str,
    db: sqlite3.Connection,
    type: str,
    any,
):
    user_id = get_user_info(db, username)[0]
    cur = db.execute(
        "SELECT users.username FROM users, contacts WHERE "
        "users.id = contacts.contact_id AND contacts.user_id = ?",
        [user_id],
    )
    for res in cur.fetchall():
        contact_username = res[0]
        ws = wss.get(contact_username, None)
        if ws is None:
            continue
        await send_data(ws, type, any)


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


def create_conversation(db: sqlite3.Connection, name: str, members) -> int:
    cur = db.cursor()

    cur.execute("BEGIN")
    try:
        # Create a new conversation
        cur.execute("INSERT INTO conversations(name) VALUES (?)", [name])
        convo_id = cur.lastrowid

        # Get the alternative userid against the members
        params = [(convo_id, get_user_info(db, m)[0]) for m in members]

        # Insert the member with it's conversation id
        cur.executemany(
            "INSERT INTO members(conversation_id, user_id) VALUES (?, ?)", params
        )
        cur.execute("COMMIT")
    except sqlite3.Error as e:
        cur.execute("ROLLBACK")
        print(e)
        return None

    return convo_id


def get_conversations(db: sqlite3.Connection, username: str):
    user_id = get_user_info(db, username)[0]
    cur = db.execute(
        "SELECT conversations.id, conversations.name FROM members, conversations WHERE "
        "conversations.id = members.conversation_id AND members.user_id = ?",
        [user_id],
    )
    res = []
    for c in cur.fetchall():
        res.append({"id": c[0], "name": c[1]})
    return res


def has_conversation(db: sqlite3.Connection, username: str, id: int):
    user_id = get_user_info(db, username)[0]
    cur = db.execute(
        "SELECT 1 FROM members WHERE user_id = ? AND conversation_id = ?", [user_id, id]
    )
    return len(cur.fetchall()) >= 1


def get_conversation_info(db: sqlite3.Connection, convo_id: int):
    res = {}

    # Get conversation name
    cur = db.execute("SELECT name FROM conversations WHERE id = ?", [convo_id])
    res["id"] = convo_id
    res["name"] = cur.fetchone()[0]
    res["members"] = []

    # Get all the members
    cur = db.execute(
        "SELECT users.username FROM users, members WHERE "
        "users.id = members.user_id AND members.conversation_id = ?",
        [convo_id],
    )
    for u in cur.fetchall():
        res["members"].append(u[0])

    return res
