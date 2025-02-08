from aiohttp import web

import src.utils.utils as utils
from src.configs.ws import WSS_KEY
from src.configs.db import DB_KEY


async def handle_add_contact(app: web.Application, username: str, event: dict):
    db = app[DB_KEY]
    wss = app[WSS_KEY]
    ws = wss[username]  # Get current username's websocket

    # Get userinfo
    user = await utils.get_user_info(db, username)
    if user is None:
        return await utils.send_error(
            ws, event["type"], f"no such user '{username}' exists"
        )

    # Get contact username
    contact_username = event.get("contact_username", None)
    if type(contact_username) is not str:
        return await utils.send_error(
            ws, event["type"], f"invalid contact_username, expected a string"
        )
    if contact_username == username:
        return await utils.send_error(
            ws, event["type"], f"cannot add itself as a contact"
        )
    contact_user = await utils.get_user_info(db, contact_username)
    if contact_user is None:
        return await utils.send_error(
            ws, event["type"], f"no such user '{contact_username}' exists"
        )

    # Check if contact_username is already a contact
    if await utils.is_contact(db, user[0], contact_user[0]):
        return await utils.send_error(
            ws, event["type"], f"'{contact_username}' is already a contact"
        )

    # Add contact_username as a contact
    await utils.add_contact(db, user[0], contact_user[0])
    await utils.send_data(
        ws,
        event["type"],
        {
            "message": f"'{contact_username}' successfully added",
            "contact": {
                "username": contact_user[1],
                "fullname": contact_user[2],
                "is_online": contact_user[4],
                "last_online": contact_user[5],
                "created_at": contact_user[6],
            },
        },
    )


async def handle_get_contacts(app: web.Application, username: str, event: dict):
    db = app[DB_KEY]
    wss = app[WSS_KEY]
    ws = wss[username]  # Get current username's websocket

    # Get userinfo
    user = await utils.get_user_info(db, username)
    if user is None:
        return await utils.send_error(
            ws, event["type"], f"no such user '{username}' exists"
        )

    # Get all the contacts
    res = await utils.get_contacts(db, user[0])
    await utils.send_data(
        ws, event["type"], {"message": "got all the contacts", "contacts": res}
    )
