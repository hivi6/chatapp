import json

import jwt
import aiohttp
from aiohttp import web

from src.configs.jwt import JWT_KEY


async def send_error(ws: web.WebSocketResponse, msg: str):
    await ws.send_json({"success": False, "error": msg})


async def send_data(ws: web.WebSocketResponse, any):
    await ws.send_json({"success": True, "data": any})


async def handle_ws_event(ws: web.WebSocketResponse, event: dict):
    type = event.get("type", None)
    if type == "ping":
        await send_data(ws, "pong")
    else:
        await send_error(ws, "no type field found in the event")


async def handle_ws(request: web.Request):
    jwtsecret = request.app[JWT_KEY]

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Check if the request has a valid login-token cookie
    login_token = request.cookies.get("login-token", None)
    if login_token is None:
        await ws.close(code=aiohttp.WSCloseCode.OK, message="login-token required")
        return ws

    try:
        decoded_jwt = jwt.decode(login_token, jwtsecret, algorithms="HS256")
        username = decoded_jwt["username"]
    except jwt.exceptions.InvalidTokenError:
        await ws.close(code=aiohttp.WSCloseCode.OK, message="invalid login-token")
        return ws

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                event = msg.json()
                if type(event) is not dict:
                    await send_error(ws, "invalid json event")
                else:
                    await handle_ws_event(ws, event)
            except json.JSONDecodeError:
                await send_error(ws, "invalid json event")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print("ws connection closed with exception %s" % ws.exception())

    return ws
