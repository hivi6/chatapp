import os
import time
import shutil
import sqlite3

from aiohttp.test_utils import AioHTTPTestCase
from argon2 import PasswordHasher

from src.app import create_app


class TestRegisterRoutes(AioHTTPTestCase):
    async def get_application(self):
        # Set a custom db path for the webapp
        self.dbpath = ".test/this_is_a_test.db"
        os.environ["DBPATH"] = self.dbpath
        shutil.rmtree(os.path.dirname(self.dbpath), ignore_errors=True)

        # Set a custom jwt secret
        self.jwtsecret = "this is a jwt secret"
        os.environ["JWTSECRET"] = self.jwtsecret

        # Create the app
        app = create_app()
        return app

    async def test_register(self):
        # Send json with valid username, password and fullname
        async with self.client.post(
            "/register", json={"username": "abc", "password": "xyz", "fullname": "123"}
        ) as res:
            self.assertEqual(res.status, 201)
            self.assertEqual(await res.text(), "registered")

        # Check in database for the inserted data
        with sqlite3.connect(self.dbpath) as conn:
            cur = conn.execute(
                "SELECT id, username, fullname, password, is_online, last_online, created_at FROM users "
                "WHERE username = 'abc'"
            )
            id, username, fullname, password, is_online, last_online, created_at = (
                cur.fetchone()
            )
            self.assertTrue(0 <= id <= 10, msg="id should be under 10")
            self.assertTrue(username == "abc", msg="username should be equal to abc")
            self.assertTrue(fullname == "123", msg="fullname should be equal to 123")
            self.assertTrue(
                len(password) != 0, msg="password hash length should not be empty"
            )
            self.assertTrue(is_online == 0, msg="is_online should be false")
            self.assertTrue(
                int(time.time() - 5) <= last_online <= int(time.time()),
                msg="last_online should be within the last 5 seconds",
            )
            self.assertTrue(
                int(time.time() - 5) <= created_at <= int(time.time()),
                msg="created_at should be within the last 5 seconds",
            )
            passhasher = PasswordHasher()
            passhasher.verify(password, "xyz")

    async def test_register_with_registered_username(self):
        # Send json with valid username, password and fullname
        async with self.client.post(
            "/register",
            json={"username": "qwerty", "password": "xyz", "fullname": "123"},
        ) as res:
            self.assertEqual(res.status, 201)
            self.assertEqual(await res.text(), "registered")

        # Send json with valid username, password and fullname but duplicate
        async with self.client.post(
            "/register",
            json={"username": "qwerty", "password": "xyz", "fullname": "123"},
        ) as res:
            self.assertEqual(res.status, 409)
            self.assertEqual(await res.text(), "username already exists")

    async def test_register_with_invalid_json(self):
        # Send invalid json
        async with self.client.post(
            "/register", data="this is an invalid json {..}[]"
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "not a valid json")

        # Send json with no username
        async with self.client.post("/register", json={}) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "username required")

        # Send json with no password
        async with self.client.post("/register", json={"username": "abc"}) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "password required")

        # Send json with no fullname
        async with self.client.post(
            "/register", json={"username": "abc", "password": "xyz"}
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "fullname required")

        # Send json with username but not valid string
        async with self.client.post(
            "/register",
            json={"username": ["abc"], "password": "xyz", "fullname": "123"},
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "username should be a string")

        # Send json with password but not valid string
        async with self.client.post(
            "/register",
            json={"username": "abc", "password": False, "fullname": "123"},
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "password should be a string")

        # Send json with fullname but not valid string
        async with self.client.post(
            "/register",
            json={"username": "abc", "password": "xyz", "fullname": 123.4},
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "fullname should be a string")

        # Send json with empty username
        async with self.client.post(
            "/register",
            json={"username": "", "password": "", "fullname": ""},
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "username should not be empty")

        # Send json with empty password
        async with self.client.post(
            "/register",
            json={"username": "abc", "password": "", "fullname": ""},
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "password should not be empty")

        # Send json with empty fullname
        async with self.client.post(
            "/register",
            json={"username": "abc", "password": "xyz", "fullname": ""},
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "fullname should not be empty")

    async def tearDownAsync(self):
        # Remove the dbpath
        shutil.rmtree(os.path.dirname(self.dbpath))
        return await super().tearDownAsync()
