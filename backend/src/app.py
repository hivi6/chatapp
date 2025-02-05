from aiohttp import web
import aiojobs.aiohttp

import src.configs.db as db_config
import src.configs.jwt as jwt_config
import src.configs.passhasher as passhasher_config
import src.routes.misc as misc_routes
import src.routes.register as register_routes
import src.routes.auth as auth_routes


def create_app():
    app = web.Application()

    # Add startup and shutdown contexts
    app.cleanup_ctx.append(db_config.db_ctx)
    app.cleanup_ctx.append(jwt_config.jwt_ctx)
    app.cleanup_ctx.append(passhasher_config.passhasher_ctx)

    # Add misc routes
    app.router.add_get("/misc/ping", misc_routes.handle_ping)

    # Add register routes
    app.router.add_post("/register", register_routes.handle_register)

    # Add authentication routes
    app.router.add_post("/auth/login", auth_routes.handle_login)

    # This is required for shielding and atomic operations
    aiojobs.aiohttp.setup(app)

    return app
