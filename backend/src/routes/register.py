import json

from aiosqlite import Connection
from aiohttp import web
from aiojobs.aiohttp import shield

from src.configs.db import DB_KEY
from src.configs.passhasher import PASSHASHER_KEY


async def insert_user(db: Connection, username: str, password: str, fullname: str):
    await db.execute(
        "INSERT INTO users(username, password, fullname) VALUES (?, ?, ?)",
        [username, password, fullname],
    )
    await db.commit()


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
    async with db.execute(
        "SELECT COUNT(*) FROM users WHERE username = ?", [username]
    ) as cursor:
        exists = (await cursor.fetchone())[0] != 0
    if exists:
        raise web.HTTPConflict(text="username already exists")

    # Convert the password to an encryted hash
    password_hash = passhaser.hash(password)

    # Insert username, password, and fullname into the database
    await shield(request, insert_user(db, username, password_hash, fullname))

    return web.HTTPCreated(text="registered")
