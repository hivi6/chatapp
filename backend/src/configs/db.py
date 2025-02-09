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
            id INTEGER,
            username TEXT NOT NULL UNIQUE,
            fullname TEXT NOT NULL,
            password TEXT NOT NULL,
            is_online INTEGER NOT NULL DEFAULT 0,
            last_online INTEGER DEFAULT (unixepoch()),
            created_at INTEGER DEFAULT (unixepoch()),
            -- constraints
            PRIMARY KEY (id)
        );

        CREATE TABLE IF NOT EXISTS contacts(
            user_id INTEGER,
            contact_id INTEGER,
            -- constraints
            PRIMARY KEY (user_id, contact_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (contact_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS conversations(
            id INTEGER,
            name TEXT NOT NULL,
            recent INTEGER DEFAULT (unixepoch()),
            -- constraints
            PRIMARY KEY (id)
        );

        CREATE TABLE IF NOT EXISTS members(
            conversation_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            -- constraints
            PRIMARY KEY (conversation_id, user_id),
            FOREIGN KEY (conversation_id) REFERENCES conversations(id),
            FOREIGN KEy (user_id) REFERENCES users(id)
        )
        """
    )

    # after this yield we have the database shutdown steps
    yield

    # Close database connection
    await db.close()
