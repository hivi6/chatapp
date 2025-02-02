from aiohttp import web


async def handle_ping(request):
    return web.Response(text="pong")
