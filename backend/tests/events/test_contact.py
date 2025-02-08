import os
import time
import shutil

import jwt
from aiohttp.test_utils import AioHTTPTestCase, ClientSession

from src.app import create_app


class TestWSContactEvent(AioHTTPTestCase):
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

    async def test_contact_event(self):
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
                # Send no contact_username
                await ws.send_json({"type": "add_contact"})
                res = await ws.receive_json()
                self.assertEqual(res["success"], False)
                self.assertEqual(res["type"], "add_contact")
                self.assertEqual(res["error"], "invalid contact_username, expected a string")

                # Send a invalid contact_username
                await ws.send_json({"type": "add_contact", "contact_username": "not-a-user"})
                res = await ws.receive_json()
                self.assertEqual(res["success"], False)
                self.assertEqual(res["type"], "add_contact")
                self.assertEqual(res["error"], f"no such user 'not-a-user' exists")

                # Send itself as a contact user
                await ws.send_json({"type": "add_contact", "contact_username": "abc"})
                res = await ws.receive_json()
                self.assertEqual(res["success"], False)
                self.assertEqual(res["type"], "add_contact")
                self.assertEqual(res["error"], "cannot add itself as a contact")

                # Add a valid contact
                await ws.send_json({"type": "add_contact", "contact_username": "pqr"})
                res = await ws.receive_json()
                self.assertEqual(res["success"], True)
                self.assertEqual(res["type"], "add_contact")
                self.assertEqual(res["data"]["message"], f"'pqr' successfully added")
                self.assertEqual(res["data"]["contact"]["username"], "pqr")
                self.assertEqual(res["data"]["contact"]["fullname"], "user2")
                self.assertEqual(res["data"]["contact"]["is_online"], False)

                # Insert an inserted contact again
                await ws.send_json({"type": "add_contact", "contact_username": "pqr"})
                res = await ws.receive_json()
                self.assertEqual(res["success"], False)
                self.assertEqual(res["type"], "add_contact")
                self.assertEqual(res["error"], f"'pqr' is already a contact")

                # Add another valid contact
                await ws.send_json({"type": "add_contact", "contact_username": "uvw"})
                res = await ws.receive_json()
                self.assertEqual(res["success"], True)
                self.assertEqual(res["type"], "add_contact")
                self.assertEqual(res["data"]["message"], f"'uvw' successfully added")
                self.assertEqual(res["data"]["contact"]["username"], "uvw")
                self.assertEqual(res["data"]["contact"]["fullname"], "user3")
                self.assertEqual(res["data"]["contact"]["is_online"], False)

    async def tearDownAsync(self):
        # Remove the dbpath
        shutil.rmtree(os.path.dirname(self.dbpath))
        return await super().tearDownAsync()
