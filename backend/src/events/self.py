from aiohttp import web

import src.utils.utils as utils
from src.configs.ws import WSS_KEY
from src.configs.db import DB_KEY


async def handle_self(app: web.Application, username: str, event: dict):
    db = app[DB_KEY]
    wss = app[WSS_KEY]
    ws = wss[username]  # Get current username's websocket

    # Get userinfo
    row = await utils.get_user_info(db, username)
    if row is None:
        return await utils.send_error(
            ws, event["type"], f"no such user '{username}' exists"
        )

    # Send userinfo
    _, username, fullname, _, is_online, last_online, created_at = row
    return await utils.send_data(
        ws,
        event["type"],
        {
            "username": username,
            "fullname": fullname,
            "is_online": bool(is_online),
            "last_online": last_online,
            "created_at": created_at,
        },
    )
