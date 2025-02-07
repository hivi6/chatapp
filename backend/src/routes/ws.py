import time
import json

import jwt
import aiohttp
from aiosqlite import Connection
from aiohttp import web

from src.configs.jwt import JWT_KEY
from src.configs.db import DB_KEY
from src.configs.ws import WSS_KEY


async def set_user_status(db: Connection, username: str, is_online: bool):
    last_online = int(time.time())
    async with db.execute(
        "UPDATE users SET is_online = ?, last_online = ?  WHERE username = ?",
        [int(is_online), last_online, username],
    ):
        await db.commit()


async def get_userinfo(db: Connection, username: str):
    async with db.execute(
        "SELECT username, fullname, is_online, last_online, created_at FROM users WHERE username = ?",
        [username],
    ) as cur:
        res = await cur.fetchall()
        if len(res) == 0:
            return None
        return res[0]


async def send_error(ws: web.WebSocketResponse, msg: str):
    await ws.send_json({"success": False, "error": msg})


async def send_data(ws: web.WebSocketResponse, any):
    await ws.send_json({"success": True, "data": any})


async def handle_ws_event(
    ws: web.WebSocketResponse, db: Connection, username: str, event: dict
):
    type = event.get("type", None)
    if type == "ping":
        await send_data(ws, "pong")
    elif type == "self":
        username, fullname, is_online, last_online, created_at = await get_userinfo(
            db, username
        )
        await send_data(
            ws,
            {
                "username": username,
                "fullname": fullname,
                "is_online": is_online,
                "last_online": last_online,
                "created_at": created_at,
            },
        )
    else:
        await send_error(ws, "no type field found in the event")


async def handle_ws(request: web.Request):
    db = request.app[DB_KEY]
    jwtsecret = request.app[JWT_KEY]
    wss = request.app[WSS_KEY]

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Check if the request has a valid login-token cookie
    login_token = request.cookies.get("login-token", None)
    if login_token is None:
        await ws.close(message="login-token required")
        return ws

    # Check if the login-token is a valid jwt
    try:
        decoded_jwt = jwt.decode(login_token, jwtsecret, algorithms="HS256")
        username = decoded_jwt["username"]
    except jwt.exceptions.InvalidTokenError:
        await ws.close(message="invalid login-token")
        return ws

    # Check if the username acquired from the login-token is valid
    check = await get_userinfo(db, username)
    if check is None:
        await ws.close(message=f"'{username}' doesn't exists")
        return ws

    try:
        # Keep track of the user's websocket
        wss[username] = ws

        # Set the user as online
        await set_user_status(db, username, True)

        # Handle all websocket events
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    event = msg.json()
                    if type(event) is not dict:
                        await send_error(ws, "invalid json event")
                    else:
                        await handle_ws_event(ws, db, username, event)
                except json.JSONDecodeError:
                    await send_error(ws, "invalid json event")
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print("ws connection closed with exception %s" % ws.exception())
    finally:
        # Remove user's websocket
        del wss[username]

        # Set the user as offline
        await set_user_status(db, username, False)

    return ws
