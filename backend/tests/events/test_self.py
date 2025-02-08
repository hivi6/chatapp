import os
import time
import shutil

import jwt
from aiohttp.test_utils import AioHTTPTestCase, ClientSession

from src.app import create_app


class TestWSSelfEvent(AioHTTPTestCase):
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

    async def test_self_event(self):
        # Send json with valid username, password and fullname
        async with self.client.post(
            "/register", json={"username": "abc", "password": "xyz", "fullname": "123"}
        ) as res:
            self.assertEqual(res.status, 201)
            self.assertEqual(await res.text(), "registered")

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

        # check websocket connection
        async with ClientSession(
            self.client.make_url(""), cookies={"login-token": login_token.value}
        ) as session:
            async with session.ws_connect("/ws") as ws:
                # Check self event
                await ws.send_json({"type": "self"})
                res = await ws.receive_json()
                self.assertEqual(res["success"], True)
                self.assertEqual(res["type"], "self")
                self.assertEqual(res["data"]["username"], "abc")
                self.assertEqual(res["data"]["fullname"], "123")
                self.assertEqual(res["data"]["is_online"], True)
                self.assertTrue(
                    int(time.time() - 5)
                    <= res["data"]["last_online"]
                    <= int(time.time()),
                    msg="last_online should be within the last 5 seconds",
                )
                self.assertTrue(
                    int(time.time() - 5)
                    <= res["data"]["created_at"]
                    <= int(time.time()),
                    msg="created_at should be within the last 5 seconds",
                )

    async def tearDownAsync(self):
        # Remove the dbpath
        shutil.rmtree(os.path.dirname(self.dbpath))
        return await super().tearDownAsync()
