import os
import time
import shutil
import sqlite3

import jwt
from aiohttp.test_utils import AioHTTPTestCase, ClientSession
from argon2 import PasswordHasher

from src.app import create_app


class TestWSRoutes(AioHTTPTestCase):
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

    async def test_ws(self):
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

        # Create a login session
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
            username = jwt_decode["username"]

        # Create websocket connection with no login_token
        async with ClientSession(self.client.make_url(""), cookies={}) as session:
            async with session.ws_connect("/ws") as ws:
                # Check if the res is closes
                res = await ws.receive()
                self.assertEqual(ws.closed, True)
                self.assertEqual(res.extra, "login-token required")

        # Create websocket connection with invalid login_token
        async with ClientSession(
            self.client.make_url(""), cookies={"login-token": "invalid-token"}
        ) as session:
            async with session.ws_connect("/ws") as ws:
                # Check if the res is closes
                res = await ws.receive()
                self.assertEqual(ws.closed, True)
                self.assertEqual(res.extra, "invalid login-token")

        # check websocket connection
        async with ClientSession(
            self.client.make_url(""), cookies={"login-token": login_token.value}
        ) as session:
            async with session.ws_connect("/ws") as ws:
                # Send invalid event
                await ws.send_str("{...}")
                res = await ws.receive_json()
                self.assertEqual(res["success"], False)
                self.assertEqual(res["error"], "invalid json event")

                # Send valid event but with no type
                await ws.send_json({})
                res = await ws.receive_json()
                self.assertEqual(res["success"], False)
                self.assertEqual(res["error"], "no type field found in the event")

                # Check ping type
                await ws.send_json({"type": "ping"})
                res = await ws.receive_json()
                self.assertEqual(res["success"], True)
                self.assertEqual(res["type"], "ping")
                self.assertEqual(res["data"], "pong")

    async def tearDownAsync(self):
        # Remove the dbpath
        shutil.rmtree(os.path.dirname(self.dbpath))
        return await super().tearDownAsync()
