import time
from aiohttp import web

import src.utils.utils as utils
from src.configs.ws import WSS_KEY
from src.configs.db import DB_KEY


async def handle_send_message(app: web.Application, username: str, event: dict):
    """
    request schema:
        {
            "type": "send_message",
            "conversation_id": 123, // Conversation id
            "content": "...",       // Message content
            "reply_id": 123,        // Optional: Message id inside the conversaation
        }

    response schema:
        error schema: This is send to the user only
            {
                "type": "send_message",
                "success": false,
                "error": "..." # Error message
            }

        success schema: This is send to all the active members of a conversation
            {
                "type": "send_message",
                "success": true,
                "data": {
                    "id": 123,                  // Message id
                    "sender_username": "...",   // Sender username
                    "conversation_id": 123,     // Conversation id
                    "reply_id": 123,            // Optional: Message id
                    "content": "...",           // Message content
                    "sent_at": 123,             // Time when message was sent
                }
            }
    """
    db = app[DB_KEY]
    wss = app[WSS_KEY]
    ws = wss[username]  # Get current username's websocket

    # Check if conversation_id is valid
    conversation_id = event.get("conversation_id", None)
    if type(conversation_id) is not int:
        return await utils.send_error(
            ws, event["type"], "expected conversation_id as integer"
        )
    if not utils.has_conversation(db, username, conversation_id):
        return await utils.send_error(
            ws,
            event["type"],
            f"{username} not part of conversation with {conversation_id} id",
        )

    # Check if message content is valid
    content = event.get("content", None)
    if type(content) is not str:
        return await utils.send_error(ws, event["type"], "expected content as string")
    if len(content) == 0:
        return await utils.send_error(
            ws, event["type"], "message content should be non empty string"
        )

    # Check if reply_id exists
    reply_id = event.get("reply_id", None)
    if reply_id is not None and type(reply_id) is not int:
        return await utils.send_error(
            ws, event["type"], "if reply_id is provided then expected integer"
        )
    if reply_id is not None and not utils.has_message(db, conversation_id, reply_id):
        return await utils.send_error(
            ws,
            event["type"],
            f"No such {reply_id} message id found in {conversation_id} conversation_id",
        )

    # Insert message in database
    sent_at = int(time.time())
    id = utils.add_message(db, conversation_id, content, reply_id, username, sent_at)
    if id is None:
        return await utils.send_error(
            ws, event["type"], "something went wrong: utils.add_message"
        )

    # send the message to all the members in the conversation
    await utils.send_data_convo(
        conversation_id,
        wss,
        db,
        event["type"],
        {
            "id": id,
            "sender_username": username,
            "conversation_id": conversation_id,
            "reply_id": reply_id,
            "content": content,
            "sent_at": sent_at,
        },
    )


async def handle_get_messages(app: web.Application, username: str, event: dict):
    """
    request schema:
        {
            "type": "get_messages",
            "conversation_id": 123, // Conversation id
            "before": 123,          // optional: All messages before the given message id
        }

    response schema:
        error schema:
            {
                "type": "get_messages",
                "success": false,
                "error": "..." # Error message
            }

        success schema: sends the most recent messages(In descending order)
            {
                "type": "get_messages",
                "success": true,
                "data": {
                    "conversation_id": 123, // conversation_id
                    "messages": [           // List of messages, max 100
                        {
                            "id": 123,                // Message id
                            "sender_username": "...", // Senders username
                            "reply_id": 123,          // Message id
                            "content": "...",         // Message content
                            "sent_at": 123,           // timestamp of when data was sent
                        },
                        ...
                    ]
                }
            }
    """
    db = app[DB_KEY]
    wss = app[WSS_KEY]
    ws = wss[username]  # Get current username's websocket

    # Check if conversation_id is valid
    conversation_id = event.get("conversation_id", None)
    if type(conversation_id) is not int:
        return await utils.send_error(
            ws, event["type"], "expected conversation_id as integer"
        )
    if not utils.has_conversation(db, username, conversation_id):
        return await utils.send_error(
            ws,
            event["type"],
            f"{username} not part of conversation with {conversation_id} id",
        )

    # Check if before is valid
    before = event.get(
        "before", 1 << 55
    )  # Assuming 2**55 is the max messages in the db
    if type(before) is not int:
        return await utils.send_error(ws, event["type"], "expected before as integer")

    messages = utils.get_messages(db, conversation_id, before)
    await utils.send_data(
        ws, event["type"], {"conversation_id": conversation_id, "messages": messages}
    )
