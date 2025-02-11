import os
import shutil

import jwt
from aiohttp.test_utils import AioHTTPTestCase, ClientSession

from src.app import create_app


class TestWSMessageEvent(AioHTTPTestCase):
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

    async def test_message(self):
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

        async with ClientSession(
            self.client.make_url(""), cookies={"login-token": login_token.value}
        ) as session:
            async with session.ws_connect("/ws") as ws:
                # Create a new conversation
                await ws.send_json(
                    {
                        "type": "create_conversation",
                        "name": "convo1",
                        "members": [],
                    }
                )
                res = await ws.receive_json()
                self.assertEqual(res["success"], True)
                self.assertEqual(res["type"], "create_conversation")
                conversation_id = res["data"]["id"]

                # Send message to the conversation
                await ws.send_json(
                    {
                        "type": "send_message",
                        "conversation_id": conversation_id,
                        "content": "hello",
                    }
                )
                res = await ws.receive_json()
                self.assertEqual(res["success"], True)
                self.assertEqual(res["type"], "send_message")
                self.assertEqual(res["data"]["id"], 1)
                self.assertEqual(res["data"]["sender_username"], "abc")
                self.assertEqual(res["data"]["conversation_id"], conversation_id)
                self.assertEqual(res["data"]["reply_id"], None)
                self.assertEqual(res["data"]["content"], "hello")

    async def tearDownAsync(self):
        # Remove the dbpath
        shutil.rmtree(os.path.dirname(self.dbpath))
        return await super().tearDownAsync()
