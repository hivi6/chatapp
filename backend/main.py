from aiohttp import web

from src.app import create_app
from src.configs.db import DBPATH_KEY

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, port=8000)