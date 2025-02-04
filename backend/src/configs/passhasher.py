from argon2 import PasswordHasher
from aiohttp import web

PASSHASHER_KEY = web.AppKey("passhasher", PasswordHasher)


async def passhasher_ctx(app: web.Application):
    app[PASSHASHER_KEY] = PasswordHasher()

    yield
