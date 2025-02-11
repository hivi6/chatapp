import os
import shutil
import asyncio

import jwt
from aiohttp.test_utils import AioHTTPTestCase, ClientSession

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

    async def setUpAsync(self):
        await super().setUpAsync()

        # Add the usernames
        async with self.client.post(
            "/register",
            json={"username": "abc", "password": "xyz", "fullname": "user1"},
        ) as res:
            self.assertEqual(res.status, 201)
            self.assertEqual(await res.text(), "registered")

        async with self.client.post(
            "/register",
            json={"username": "pqr", "password": "xyz", "fullname": "user2"},
        ) as res:
            self.assertEqual(res.status, 201)
            self.assertEqual(await res.text(), "registered")

        async with self.client.post(
            "/register",
            json={"username": "uvw", "password": "xyz", "fullname": "user3"},
        ) as res:
            self.assertEqual(res.status, 201)
            self.assertEqual(await res.text(), "registered")

    async def test_ws(self):
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

    async def test_ws_user_status(self):
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
            abc_login_token = login_token.value

        # Create a login session
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
            pqr_login_token = login_token.value

        # Make websocket connection as abc
        async with ClientSession(
            self.client.make_url(""), cookies={"login-token": abc_login_token}
        ) as abc_session:
            async with abc_session.ws_connect("/ws") as abc_ws:
                # Add a contact
                await abc_ws.send_json({"type": "add_contact", "contact_username": "pqr"})
                res = await abc_ws.receive_json()
                self.assertEqual(res["success"], True)
                self.assertEqual(res["type"], "add_contact")
                self.assertEqual(res["data"]["message"], f"'pqr' successfully added")
                self.assertEqual(res["data"]["contact"]["username"], "pqr")
                self.assertEqual(res["data"]["contact"]["fullname"], "user2")
                self.assertEqual(res["data"]["contact"]["is_online"], False)
                
                # Now make websocket connection as pqr
                async with ClientSession(
                    self.client.make_url(""), cookies={"login-token": pqr_login_token}
                ) as pqr_session:
                    async with pqr_session.ws_connect("/ws") as _:
                        # Now as pqr has connect, check if abc_ws is getting any is_online event
                        res = await abc_ws.receive_json()
                        self.assertEqual(res["success"], True)
                        self.assertEqual(res["type"], "user_status")
                        self.assertEqual(res["data"]["username"], "pqr")
                        self.assertEqual(res["data"]["is_online"], True)

                # Now again check abc_ws, it should have information regarding
                # that pqr is now offline
                res = await abc_ws.receive_json()
                self.assertEqual(res["success"], True)
                self.assertEqual(res["type"], "user_status")
                self.assertEqual(res["data"]["username"], "pqr")
                self.assertEqual(res["data"]["is_online"], False)


    async def tearDownAsync(self):
        # Remove the dbpath
        shutil.rmtree(os.path.dirname(self.dbpath))
        return await super().tearDownAsync()
