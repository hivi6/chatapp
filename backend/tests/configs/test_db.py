import os
import shutil
import sqlite3

from aiohttp.test_utils import AioHTTPTestCase

from src.app import create_app
from src.configs.db import DBPATH_KEY, DB_KEY


class TestDBConfig(AioHTTPTestCase):
    async def get_application(self):
        # Set a custom db path for the webapp
        self.dbpath = ".test/this_is_a_test.db"
        os.environ["DBPATH"] = self.dbpath
        shutil.rmtree(os.path.dirname(self.dbpath), ignore_errors=True)

        # Create the app
        app = create_app()
        return app

    async def test_db(self):
        # Check if dbpath is correct
        self.assertEqual(self.server.app[DBPATH_KEY], os.environ["DBPATH"])
        self.assertEqual(self.server.app[DBPATH_KEY], self.dbpath)

        # Check if the tables are created
        final_tables = ["users", "contacts", "conversations", "members"]
        with sqlite3.connect(self.dbpath) as conn:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            tables = cur.fetchall()
            self.assertEqual(set(final_tables), set([t[0] for t in tables]))

    async def tearDownAsync(self):
        # Remove the dbpath
        shutil.rmtree(os.path.dirname(self.dbpath))
        return await super().tearDownAsync()
