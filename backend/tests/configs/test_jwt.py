import os
import shutil

from aiohttp.test_utils import AioHTTPTestCase

from src.app import create_app
from src.configs.jwt import JWT_KEY


class TestJWTConfig(AioHTTPTestCase):
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

    async def test_jwt(self):
        # Check if jwt secret is correctly part of the app config
        self.assertEqual(self.jwtsecret, self.app[JWT_KEY])

    async def tearDownAsync(self):
        # Remove the dbpath
        shutil.rmtree(os.path.dirname(self.dbpath))
        return await super().tearDownAsync()
