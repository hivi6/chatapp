import json

import jwt
import aiohttp
from aiohttp import web

from src.configs.jwt import JWT_KEY
from src.configs.db import DB_KEY
from src.configs.ws import WSS_KEY
import src.utils.utils as utils
from src.events.ping import handle_ping
from src.events.self import handle_self
from src.events.contact import handle_add_contact, handle_get_contacts


async def handle_ws_event(app: web.Application, username: str, event: dict):
    ws = app[WSS_KEY][username]
    type = event.get("type", None)

    # Handle event type
    if type == "ping":
        await handle_ping(app, username, event)
    elif type == "self":
        await handle_self(app, username, event)
    elif type == "add_contact":
        await handle_add_contact(app, username, event)
    elif type == "get_contacts":
        await handle_get_contacts(app, username, event)
    else:
        await utils.send_error(ws, "root", f"no type field found in the event")


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
    check = await utils.get_user_info(db, username)
    if check is None:
        await ws.close(message=f"'{username}' doesn't exists")
        return ws

    # Check if websocket is already connected
    # There can be only one websocket connection per user
    if username in wss:
        await ws.close(
            message=f"'{username}' is already connected. Cannot have multiple instance"
        )
        return ws

    try:
        # Keep track of the user's websocket
        wss[username] = ws

        # Set the user as online
        await utils.set_user_status(db, username, True)

        # Handle all websocket events
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    event = msg.json()
                    if type(event) is not dict:
                        await utils.send_error(ws, "root", "invalid json event")
                    else:
                        await handle_ws_event(request.app, username, event)
                except json.JSONDecodeError:
                    await utils.send_error(ws, "root", "invalid json event")
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print("ws connection closed with exception %s" % ws.exception())
    finally:
        # Remove user's websocket
        del wss[username]

        # Set the user as offline
        await utils.set_user_status(db, username, False)

    return ws
