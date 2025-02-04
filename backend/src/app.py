from aiohttp import web


import src.configs.db as db_config
import src.configs.jwt as jwt_config
import src.routes.misc as misc_routes


def create_app():
    app = web.Application()

    # Add startup and shutdown contexts
    app.cleanup_ctx.append(db_config.db_ctx)
    app.cleanup_ctx.append(jwt_config.jwt_ctx)

    # Add misc routes
    app.router.add_get("/misc/ping", misc_routes.handle_ping)

    return app
