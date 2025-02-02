from aiohttp import web

import backend.routes.misc as misc_routes


def create_app():
    app = web.Application()

    # Add misc routes
    app.router.add_get("/misc/ping", misc_routes.handle_ping)

    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, port=8000)
