import os
import shutil

import jwt
from aiohttp.test_utils import AioHTTPTestCase, ClientSession

from src.app import create_app


class TestWSConversationEvent(AioHTTPTestCase):
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

    async def test_conversation_event(self):
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
                # Create a new conversation
                await ws.send_json(
                    {
                        "type": "create_conversation",
                        "name": "convo1",
                        "members": ["pqr"],
                    }
                )
                res = await ws.receive_json()
                self.assertEqual(res["success"], True)
                self.assertEqual(res["type"], "create_conversation")
                self.assertEqual(res["data"]["name"], "convo1")
                self.assertTrue(set(res["data"]["members"]) == {"abc", "pqr"})
                convo1_id = res["data"]["id"]

                # Get all conversation
                await ws.send_json({"type": "get_conversations"})
                res = await ws.receive_json()
                self.assertEqual(res["success"], True)
                self.assertEqual(res["type"], "get_conversations")
                self.assertEqual(res["data"][0]["id"], convo1_id)
                self.assertEqual(res["data"][0]["name"], "convo1")

    async def tearDownAsync(self):
        # Remove the dbpath
        shutil.rmtree(os.path.dirname(self.dbpath))
        return await super().tearDownAsync()
