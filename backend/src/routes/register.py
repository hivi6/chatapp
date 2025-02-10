import json
import sqlite3

from aiohttp import web

from src.configs.db import DB_KEY
from src.configs.passhasher import PASSHASHER_KEY


def insert_user(
    db: sqlite3.Connection, username: str, password: str, fullname: str
) -> str:
    cur = db.cursor()
    cur.execute("BEGIN")
    try:
        cur.execute(
            "INSERT INTO users(username, password, fullname) VALUES (?, ?, ?)",
            [username, password, fullname],
        )
        cur.execute("COMMIT")
    except sqlite3.Error as e:
        cur.execute("ROLLBACK")
        return "something went wrong: insert_user"
    return None


async def handle_register(request: web.Request):
    db = request.app[DB_KEY]
    passhaser = request.app[PASSHASHER_KEY]

    # Check if payload is a valid json
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise web.HTTPBadRequest(text="not a valid json")

    # Check if username, password, and fullname exists in the payload
    if "username" not in payload:
        raise web.HTTPBadRequest(text="username required")
    if "password" not in payload:
        raise web.HTTPBadRequest(text="password required")
    if "fullname" not in payload:
        raise web.HTTPBadRequest(text="fullname required")

    # Check if username, password and fullname are strings
    username, password, fullname = (
        payload["username"],
        payload["password"],
        payload["fullname"],
    )
    if type(username) is not str:
        raise web.HTTPBadRequest(text="username should be a string")
    if type(password) is not str:
        raise web.HTTPBadRequest(text="password should be a string")
    if type(fullname) is not str:
        raise web.HTTPBadRequest(text="fullname should be a string")

    # Check if username, password and fullname are not empty
    if len(username) == 0:
        raise web.HTTPBadRequest(text="username should not be empty")
    if len(password) == 0:
        raise web.HTTPBadRequest(text="password should not be empty")
    if len(fullname) == 0:
        raise web.HTTPBadRequest(text="fullname should not be empty")

    # Check if username already exists
    exists = False
    cur = db.execute("SELECT COUNT(*) FROM users WHERE username = ?", [username])
    exists = cur.fetchone()[0] != 0
    if exists:
        raise web.HTTPConflict(text="username already exists")

    # Convert the password to an encryted hash
    password_hash = passhaser.hash(password)

    # Insert username, password, and fullname into the database
    err = insert_user(db, username, password_hash, fullname)
    if err is not None:
        raise web.HTTPServerError(text=err)

    return web.HTTPCreated(text="registered")
