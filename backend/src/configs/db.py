import os
import sqlite3

from aiohttp import web

DB_KEY = web.AppKey("db", sqlite3.Connection)
DBPATH_KEY = web.AppKey("dbpath", str)


async def db_ctx(app: web.Application):
    # Get the database path
    db_path = os.environ.get("DBPATH", ".data/chatapp.db")
    dirname = os.path.dirname(db_path)
    os.makedirs(dirname, exist_ok=True)
    app[DBPATH_KEY] = db_path

    # Connect to database
    db = sqlite3.connect(db_path, isolation_level=None)
    app[DB_KEY] = db

    # Add the required tables
    cur = db.cursor()
    cur.execute("BEGIN")
    try:
        cur.execute(
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
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts(
                user_id INTEGER,
                contact_id INTEGER,
                -- constraints
                PRIMARY KEY (user_id, contact_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (contact_id) REFERENCES users(id)
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations(
                id INTEGER,
                name TEXT NOT NULL,
                recent INTEGER DEFAULT (unixepoch()),
                -- constraints
                PRIMARY KEY (id)
            );
            """
        )
        cur.execute(
            """
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
        cur.execute("COMMIT")
    except sqlite3.Error as e:
        cur.execute("ROLLBACK")
        print("Something went wrong while setting up database schema")
        print(e)
        raise e

    # after this yield we have the database shutdown steps
    yield

    # Close database connection
    db.close()
