from aiohttp import web

WSS_KEY = web.AppKey(
    "wss", dict[str, web.WebSocketResponse]
)  # map of all the users and there websocket


async def wss_ctx(app: web.Application):
    # Add the dictionary to store websocket per username
    app[WSS_KEY] = dict()

    yield

    # Remove all the websocket
    for username, ws in app[WSS_KEY].items():
        await ws.close()
