import time

from aiohttp import web
from aiosqlite import Connection


async def send_error(ws: web.WebSocketResponse, type: str, msg: str):
    await ws.send_json({"success": False, "type": type, "error": msg})


async def send_data(ws: web.WebSocketResponse, type: str, any):
    await ws.send_json({"success": True, "type": type, "data": any})


async def get_user_info(db: Connection, username: str):
    async with db.execute(
        "SELECT id, username, fullname, password, is_online, last_online, created_at FROM users "
        "WHERE username = ?",
        [username],
    ) as cur:
        res = await cur.fetchall()
        if len(res) == 0:
            return None
    return res[0]


async def set_user_status(db: Connection, username: str, is_online: bool):
    last_online = int(time.time())
    async with db.execute(
        "UPDATE users SET is_online = ?, last_online = ?  WHERE username = ?",
        [int(is_online), last_online, username],
    ):
        await db.commit()
