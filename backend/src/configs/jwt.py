from aiohttp import web

JWT_KEY = web.AppKey("jwt", str)


async def jwt_ctx(app: web.Application):
    app[JWT_KEY] = "some random jwt secret that needs tom be in an env file"

    yield