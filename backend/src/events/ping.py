from aiohttp import web

import src.utils.utils as utils
from src.configs.ws import WSS_KEY


async def handle_ping(app: web.Application, username: str, event: dict):
    """
    request schema:
        {
            "type": "ping"
        }
    """
    wss = app[WSS_KEY]
    ws = wss[username]  # Get current username's websocket

    await utils.send_data(ws, event["type"], "pong")
