import os

from aiohttp import web
import aiohttp_cors

from src.app import create_app

if __name__ == "__main__":
    app = create_app()

    # Get CORS_ALLOW_ORIGIN environment variable
    CORS_ALLOW_ORIGIN = os.environ.get("CORS_ALLOW_ORIGIN", "http://localhost:5173")

    # Configure default CORS settings.
    cors = aiohttp_cors.setup(
        app,
        defaults={
            CORS_ALLOW_ORIGIN: aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )

    # Configure CORS on all routes.
    for route in list(app.router.routes()):
        cors.add(route)

    web.run_app(app, port=8000)
