import os

from aiohttp import web

JWT_KEY = web.AppKey("jwt", str)


async def jwt_ctx(app: web.Application):
    # Get jwtsecret from environment variable
    jwtsecret = os.environ.get("JWTSECRET", "this is a demo jwt secret")
    app[JWT_KEY] = jwtsecret

    yield
