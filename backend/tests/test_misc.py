from aiohttp.test_utils import AioHTTPTestCase

from backend.app import create_app


class TestMiscRoutes(AioHTTPTestCase):
    async def get_application(self):
        return create_app()

    async def test_ping(self):
        async with self.client.get("/misc/ping") as res:
            self.assertEqual(res.status, 200)

            text = await res.text()
            self.assertEqual(text, "pong")
