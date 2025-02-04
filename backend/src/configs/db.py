import os

import aiosqlite
from aiohttp import web

DB_KEY = web.AppKey("db", aiosqlite.Connection)
DBPATH_KEY = web.AppKey("dbpath", str)


async def db_ctx(app: web.Application):
    # Get the database path
    db_path = os.environ.get("DBPATH", ".data/chatapp.db")
    dirname = os.path.dirname(db_path)
    os.makedirs(dirname, exist_ok=True)
    app[DBPATH_KEY] = db_path

    # Connect to database
    db = await aiosqlite.connect(db_path)
    app[DB_KEY] = db

    # Add the required tables
    await db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            fullname TEXT NOT NULL,
            password TEXT NOT NULL,
            is_online INTEGER NOT NULL DEFAULT 0,
            last_online INTEGER DEFAULT (unixepoch())
        )
        """
    )

    # after this yield we have the database shutdown steps
    yield

    # Close database connection
    await db.close()
