from aiohttp import web

import src.utils.utils as utils
from src.configs.ws import WSS_KEY
from src.configs.db import DB_KEY


async def handle_create_conversation(app: web.Application, username: str, event: dict):
    """
    request schema:
        {
            "type": "create_conversation",
            "members": [ // Array of usernames, self username not included
                "user1",
                "user2",
                ...
            ]
        }

    response schema:
        error schema: This is only send to the request websocket
            {
                "type": "create_conversation",
                "success": false,
                "error": "..." # Error message
            }

        success schema: This data is send to all the active members of the conversation
            {
                "type": "create_conversation",
                "success": true,
                "data": {           // Information of created conversation
                    "id": 123,      // Conversation id; unique
                    "name": "...",  // Conversation name; might not be unique
                    "members": [    // Members of the conversation
                        "self",
                        "user1",
                        "user2",
                        ...
                    ]
                }
            }
    """
    db = app[DB_KEY]
    wss = app[WSS_KEY]
    ws = wss[username]  # Get current username's websocket

    # Check if members are valid member type
    name = event.get("name", None)
    members = event.get("members", None)
    if type(name) is not str or len(name) == 0:
        return await utils.send_error(
            ws, event["type"], "name value expected as a non zero string"
        )
    if type(members) is not list:
        return await utils.send_error(
            ws, event["type"], "members value expected a list"
        )

    # Get all the unique usernames and include self
    members = list(set(members + [username]))
    # Check if all the member are string type
    if set([type(m) for m in members]) != {str}:
        return await utils.send_error(
            ws, event["type"], "members should be a list of string"
        )

    # Check if members are valid username
    for m in members:
        m_user = utils.get_user_info(db, m)
        if m_user is None:
            return await utils.send_error(
                ws, event["type"], f"'{m}' is not a valid username"
            )

    # Create a new conversation
    id = utils.create_conversation(db, name, members)
    if id is None:
        return await utils.send_error(
            ws, event["type"], f"something went wrong: utils.create_conversation"
        )

    # Send to all the active members
    await utils.send_data_convo(
        id, wss, db, event["type"], {"id": id, "name": name, "members": members}
    )


async def handle_get_conversations(app: web.Application, username: str, event: dict):
    """
    request schema:
        {
            "type": "get_conversations"
        }

    response schema:
        error schema:
            {
                "type": "get_conversations",
                "success": false,
                "error": "..." # Error message
            }

        success schema:
            {
                "type": "get_conversations",
                "success": true,
                "data": [
                    { // This is the first conversation; no members included
                        "id": 123,
                        "name": "..."
                    },
                    { // This is the second conversation
                        ...
                    },
                    ...
                ]
            }
    """
    db = app[DB_KEY]
    wss = app[WSS_KEY]
    ws = wss[username]  # Get current username's websocket

    # Get all the conversations
    res = utils.get_conversations(db, username)

    await utils.send_data(ws, event["type"], res)


async def handle_get_conversation_info(
    app: web.Application, username: str, event: dict
):
    """
    request schema:
        {
            "type": "get_conversation_info",
            "id": 123 // Conversation id
        }

    response schema:
        error schema:
            {
                "type": "get_conversation_info",
                "success": false,
                "error": "..." # Error message
            }

        success schema:
            {
                "type": "get_conversation_info",
                "success": true,
                "data": {
                    "id": 123,
                    "name": "...",
                    "members": [ // All the members in the conversation
                        "user1",
                        "user2",
                        ...
                    ]
                }
            }
    """
    db = app[DB_KEY]
    wss = app[WSS_KEY]
    ws = wss[username]  # Get current username's websocket

    # Get conversation id
    convo_id = event.get("id", None)
    if type(convo_id) is not int:
        return await utils.send_error(ws, event["type"], "id is required as int")

    # Check if username is part of the conversation
    if not utils.has_conversation(db, username, convo_id):
        return await utils.send_error(
            ws,
            event["type"],
            f"{username} is not part of any conversation with {convo_id} id",
        )

    # Get conversation information
    res = utils.get_conversation_info(db, convo_id)
    await utils.send_data(ws, event["type"], res)
