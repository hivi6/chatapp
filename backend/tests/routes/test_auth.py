import os
import time
import shutil
import sqlite3

import jwt
from aiohttp.test_utils import AioHTTPTestCase, ClientSession
from argon2 import PasswordHasher

from src.app import create_app


class TestAuthRoutes(AioHTTPTestCase):
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

    async def test_login(self):
        # Send json with valid username, password and fullname
        async with self.client.post(
            "/register", json={"username": "abc", "password": "xyz", "fullname": "123"}
        ) as res:
            self.assertEqual(res.status, 201)
            self.assertEqual(await res.text(), "registered")

        # Check in database for the inserted data
        with sqlite3.connect(self.dbpath) as conn:
            cur = conn.execute(
                "SELECT id, username, fullname, password, is_online, last_online FROM users "
                "WHERE username = 'abc'"
            )
            id, username, fullname, password, is_online, last_online = cur.fetchone()
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
            passhasher = PasswordHasher()
            passhasher.verify(password, "xyz")

        # Check if login is working
        async with self.client.post(
            "/auth/login", json={"username": "abc", "password": "xyz"}
        ) as res:
            self.assertEqual(res.status, 202)
            self.assertEqual(await res.text(), "login successful")
            login_token = res.cookies.get("login-token")
            jwt_decode = jwt.decode(
                login_token.value, self.jwtsecret, algorithms="HS256"
            )
            self.assertEqual(jwt_decode["username"], "abc")

    async def test_login_with_invalid_values(self):
        # Send invalid json
        async with self.client.post(
            "/auth/login", data="this is an invalid json {..}[]"
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "not a valid json")

        # Send json with no username
        async with self.client.post("/auth/login", json={}) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "username required")

        # Send json with no password
        async with self.client.post("/auth/login", json={"username": "abc"}) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "password required")

        # Send json with username but not valid string
        async with self.client.post(
            "/auth/login",
            json={"username": ["abc"], "password": "xyz"},
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "username should be a string")

        # Send json with password but not valid string
        async with self.client.post(
            "/auth/login",
            json={"username": "abc", "password": False},
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "password should be a string")

        # Send json with empty username
        async with self.client.post(
            "/auth/login",
            json={"username": "", "password": ""},
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "username should not be empty")

        # Send json with empty password
        async with self.client.post(
            "/auth/login",
            json={"username": "abc", "password": ""},
        ) as res:
            self.assertEqual(res.status, 400)
            self.assertEqual(await res.text(), "password should not be empty")

        # register a new user
        async with self.client.post(
            "/register", json={"username": "pqr", "password": "xyz", "fullname": "123"}
        ) as res:
            self.assertEqual(res.status, 201)
            self.assertEqual(await res.text(), "registered")

        # Check if login is working
        async with self.client.post(
            "/auth/login", json={"username": "pqr", "password": "xyz"}
        ) as res:
            self.assertEqual(res.status, 202)
            self.assertEqual(await res.text(), "login successful")
            login_token = res.cookies.get("login-token")
            jwt_decode = jwt.decode(
                login_token.value, self.jwtsecret, algorithms="HS256"
            )
            self.assertEqual(jwt_decode["username"], "pqr")

        # Login should not work with incorrect username
        async with self.client.post(
            "/auth/login", json={"username": "uvw", "password": "xyz"}
        ) as res:
            self.assertEqual(res.status, 401)
            self.assertEqual(await res.text(), "mismatch username and password")

        # Login should not work with incorrect password
        async with self.client.post(
            "/auth/login", json={"username": "pqr", "password": "123"}
        ) as res:
            self.assertEqual(res.status, 401)
            self.assertEqual(await res.text(), "mismatch username and password")

    async def test_verify(self):
        # Create a new user
        async with self.client.post(
            "/register", json={"username": "pqr", "password": "xyz", "fullname": "123"}
        ) as res:
            self.assertEqual(res.status, 201)
            self.assertEqual(await res.text(), "registered")

        # Check if login is working
        async with self.client.post(
            "/auth/login", json={"username": "pqr", "password": "xyz"}
        ) as res:
            self.assertEqual(res.status, 202)
            self.assertEqual(await res.text(), "login successful")
            login_token = res.cookies.get("login-token")
            jwt_decode = jwt.decode(
                login_token.value, self.jwtsecret, algorithms="HS256"
            )
            self.assertEqual(jwt_decode["username"], "pqr")

        # # Don't know but below code is not working
        # # Check if verify is working
        # async with self.client.get("/auth/verify") as res:
        #     self.assertEqual(res.status, 200)

        async with ClientSession(
            self.client.make_url(""), cookies={"login-token": login_token.value}
        ) as session:
            async with session.get("/auth/verify") as res:
                self.assertEqual(res.status, 200)
                self.assertEqual(await res.text(), "Hello, pqr")

    async def test_verify_with_invalid_token(self):
        async with ClientSession(self.client.make_url("")) as session:
            async with session.get("/auth/verify") as res:
                self.assertEqual(res.status, 401)
                self.assertEqual(await res.text(), "login-token required")

        async with ClientSession(
            self.client.make_url(""), cookies={"login-token": "wrong login token"}
        ) as session:
            async with session.get("/auth/verify") as res:
                self.assertEqual(res.status, 401)
                self.assertEqual(await res.text(), "invalid login-token")

    async def tearDownAsync(self):
        # Remove the dbpath
        shutil.rmtree(os.path.dirname(self.dbpath))
        return await super().tearDownAsync()
