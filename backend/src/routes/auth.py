import json
import time

import jwt
import argon2
from aiosqlite import Connection
from aiohttp import web
from aiojobs.aiohttp import shield

from src.configs.db import DB_KEY
from src.configs.passhasher import PASSHASHER_KEY
from src.configs.jwt import JWT_KEY


async def update_password_hash(db: Connection, username: str, password: str):
    await db.execute(
        "UPDATE users SET password = ? WHERE username = ?", [password, username]
    )
    await db.commit()


async def handle_login(request: web.Request):
    db = request.app[DB_KEY]
    passhasher = request.app[PASSHASHER_KEY]
    jwtsecret = request.app[JWT_KEY]

    # Check if payload is a valid json
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise web.HTTPBadRequest(text="not a valid json")

    # Check if username, and password exists in the payload
    if "username" not in payload:
        raise web.HTTPBadRequest(text="username required")
    if "password" not in payload:
        raise web.HTTPBadRequest(text="password required")

    # Check if username, and password are strings
    username, password = (
        payload["username"],
        payload["password"],
    )
    if type(username) is not str:
        raise web.HTTPBadRequest(text="username should be a string")
    if type(password) is not str:
        raise web.HTTPBadRequest(text="password should be a string")

    # Check if username, and password are not empty
    if len(username) == 0:
        raise web.HTTPBadRequest(text="username should not be empty")
    if len(password) == 0:
        raise web.HTTPBadRequest(text="password should not be empty")

    # Check if password is correct
    valid_pass = False
    async with db.execute(
        "SELECT password FROM users WHERE username = ?", [username]
    ) as cur:
        password_hashes = await cur.fetchall()
        if len(password_hashes) == 1:
            passhash = password_hashes[0][0]
            try:
                passhasher.verify(passhash, password)
                valid_pass = True
            except argon2.exceptions.VerificationError:
                pass
    if not valid_pass:
        raise web.HTTPUnauthorized(text="mismatch username and password")

    # Check if password needs rehash for security reasons
    if passhasher.check_needs_rehash(passhash):
        new_passhash = passhasher.hash(password)
        await shield(request, update_password_hash(db, username, new_passhash))

    # Generate a jwt login token
    max_age = 3600
    expire_time = int(time.time()) + max_age
    encoded_jwt = jwt.encode({"username": username, "exp": expire_time}, jwtsecret)

    # Create a response with the login-token jwt cookie
    response = web.Response(text="login successful", status=202)
    response.set_cookie(
        "login-token", encoded_jwt, max_age=max_age, secure=True, httponly=True
    )
    return response
