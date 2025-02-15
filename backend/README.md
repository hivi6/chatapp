# backend

A chatapp backend written in python.

## Environment variables

The backend takes in 2 environment variables:

1. DBPATH: Path to where the database needs to be created, or used. defaults to `.data/chatapp.db`
2. JWTSECRET: This is the jwt secret used for creating login-token's. defaults to `this is a demo jwt secret`
3. CORS_ALLOW_ORIGIN: This is the cors allow origin, defaults to `http://localhost:5173` (This is only for main.py not for test.py)

## Setting up requirements

Assuming that you are in the chatapp root directory. Run the command below:

```bash
python3 -m venv .pyenv     # Create a new python environment
source .pyenv/bin/activate # Activate the python environment
pip install -r backend/requirements.txt # This will install all the requirements
```

## Running the backend

Assuming that you are in the chatapp root directory. Run the command below:

```bash
source .pyenv/bin/activate
python3 backend/main.py
```

To add the environment variables use the following command

```bash
source .pyenv/bin/activate
DBPATH=.data/custom_db_path.db JWTSECRET="This is a custom jwt secret" python3 backend/main.py
```

## Testing the backend

Assuming that you are in the chatapp root directory. Run the command below:

```bash
source .pyenv/bin/activate
python3 backend/test.py
```

## REST API docs

The REST API to the chatapp backend is given below

### Misc routes

#### Ping

_REQUEST_

`GET /misc/ping`

```
curl -i localhost:8000/misc/ping
```

_RESPONSE_

```
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Content-Length: 4
Date: Thu, 13 Feb 2025 14:41:46 GMT
Server: Python/3.11 aiohttp/3.11.11

pong
```

### Register routes

#### Register

_REQUEST_

`POST /register`

```
curl -i localhost:8000/register -d '{
    "username": "hizz",
    "password": "xyz",
    "fullname": "Snakey"
}'
```

_RESPONSE_

```
HTTP/1.1 201 Created
Content-Type: text/plain; charset=utf-8
Content-Length: 10
Date: Thu, 13 Feb 2025 14:54:58 GMT
Server: Python/3.11 aiohttp/3.11.11

registered
```

### Auth routes

#### Login

_REQUEST_

`POST /auth/login`

```
curl -i localhost:8000/auth/login -d '{
    "username": "hizz",
    "password": "xyz"
}'
```

_RESPONSE_

```
HTTP/1.1 202 Accepted
Content-Type: text/plain; charset=utf-8
Content-Length: 16
Set-Cookie: login-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImhpenoiLCJleHAiOjE3Mzk0NjIzNzV9.-NN3UMSk03aCmaBQqwfJbKaoVGij387wG29FyJaYgtI; HttpOnly; Max-Age=3600; Path=/; Secure
Date: Thu, 13 Feb 2025 14:59:35 GMT
Server: Python/3.11 aiohttp/3.11.11

login successful
```

Here in respose a cookie is sent, which is a jwt login-token.

#### Verify

_REQUEST_

`GET /auth/verify`

```
curl -i localhost:8000/auth/verify --cookie 'login-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImhpenoiLCJleHAiOjE3Mzk0NjIzNzV9.-NN3UMSk03aCmaBQqwfJbKaoVGij387wG29FyJaYgtI'
```

_RESPONSE_

```
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Content-Length: 11
Date: Thu, 13 Feb 2025 15:03:51 GMT
Server: Python/3.11 aiohttp/3.11.11

Hello, hizz
```

### Ws routes

`GET /ws`

For a connection with websocket, we have to make sure that a valid login-token cookie is part of the websocket request.
When a websocket connection is establish, it sends a event with type as `user_status` to the contact usernames.

#### user_status event

- About:
  - Send user status to all the contact usernames, when the user gets online or offline.
- Trigger:
  - This event response is sent when a user successfully connects or disconnects from a websocket.
- To:
  - This event is sent to all the active contact username connections.

_EVENT RESPONSE_

```javascript
{
    "type": "user_status"
    "success": true,
    "data": {
        "username": "user1",
        "is_online": true
    }
}
```

#### self event

- About:
  - Send user information to the connected websocket.
- Trigger:
  - This event response is sent when an user makes an event request to the server.
- To:
  - This event is sent as a response to the request made by the user.

_EVENT REQUEST_

```javascript
{
  "type": "self"
}
```

_EVENT RESPONSE_

Success:

```javascript
{
  "type": "self",
  "success": true,
  "data": {
    // Information of self
    "username": "...",
    "fullname": "...",
    "is_online": true,
    "last_online": 123,
    "created_at": 123
  }
}
```

Error:

```javascript
{
  "type": "self",
  "success": false,
  "error": "..." // Error message
}
```

#### ping event

- About:
  - Just send pong. Similar to `/misc/ping`
- Trigger:
  - This event response is sent when an user makes an event request to the server.
- To:
  - This event is sent as a response to the request made by the user.

_EVENT REQUEST_

```javascript
{
  "type": "ping"
}
```

_EVENT RESPONSE_

```javascript
{
  "type": "ping",
  "success": true,
  "data": "pong"
}
```

#### add_contact event

- About:
  - Create a new contact.
- Trigger:
  - This event response is sent when an user makes an event request to the server.
- To:
  - This event is sent as a response to the request made by the user.

_EVENT REQUEST_

```javascript
{
  "type": "add_contact",
  "contact_username": "..." // This is the username that you want to create contact
}
```

_EVENT RESPONSE_

Success:

```javascript
{
  "success": true,
  "type": "add_contact",
  "data": {
    "message": "...", // This is the message saying that contact is added
    "contact": {
      // This is the contact information that was added
      "username": "...",
      "fullname": "...",
      "is_online": true,
      "last_online": 123, // Integer value in unix epoch seconds
      "created_at": 123 // Integer value in unix epoch seconds
    }
  }
}
```

Error:

```javascript
{
  "success": false,
  "type": "add_contact",
  "error": "..." // This is the error message
}
```

#### get_contacts event

- About:
  - Send all the contacts of the connected user.
- Trigger:
  - This event response is sent when an user makes an event request to the server.
- To:
  - This event is sent as a response to the request made by the user.

_EVENT REQUEST_

```javascript
{
  "type": "get_contacts"
}
```

_EVENT RESPONSE_

Success:

```javascript
{
    "success": false,
    "type": "get_contacts",
    "data": {
        "message": "...", // Message stating that contacts are successfully fetch
        "contacts": [ // Array of usernames
            "user1",
            "user2",
            ...
        ]
    }
}
```

Error:

```javascript
{
  "success": false,
  "type": "get_contacts",
  "error": "..." // Message of the error
}
```

#### create_conversation event

- About:
  - Create a new conversation using the list of users.
- Trigger:
  - This event response is sent when an user makes an event request to the server.
- To:
  - This event to all the users part of the conversation.

_EVENT REQUEST_

```javascript
{
    "type": "create_conversation",
    "members": [ // Array of usernames, self username not included
        "user1",
        "user2",
        ...
    ]
}
```

_EVENT RESPONSE_

Success:

```javascript
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
```

Error:

```javascript
{
  "type": "create_conversation",
  "success": false,
  "error": "..." // Error message
}
```

#### get_conversations event

- About:
  - Send list of all the conversations of a user
- Trigger:
  - This event response is sent when an user makes an event request to the server.
- To:
  - This event is sent as a response to the request made by the user.

_EVENT REQUEST_

```javascript
{
  "type": "get_conversations"
}
```

_EVENT RESPONSE_

Success:

```javascript
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
```

Error:

```javascript
{
  "type": "get_conversations",
  "success": false,
  "error": "..." // Error message
}
```

#### get_conversation_info event

- About:
  - Send information about a given conversation.
- Trigger:
  - This event response is sent when an user makes an event request to the server.
- To:
  - This event is sent as a response to the request made by the user.

_EVENT REQUEST_

```javascript
{
  "type": "get_conversation_info",
  "id": 123 // Conversation id
}
```

_EVENT RESPONSE_

Success:

```javascript
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
```

Error:

```javascript
{
  "type": "get_conversation_info",
  "success": false,
  "error": "..." // Error message
}
```

#### send_message event

- About:
  - Send message to a given conversation
- Trigger:
  - This event response is sent when an user makes an event request to the server.
- To:
  - This event is sent as a response to all the members of a conversation.

_EVENT REQUEST_

```javascript
{
  "type": "send_message",
  "conversation_id": 123, // Conversation id
  "content": "...", // Message content
  "reply_id": 123 // Optional: Message id inside the conversaation
}
```

_EVENT RESPONSE_

Success:

```javascript
{
  "type": "send_message",
  "success": true,
  "data": {
    "id": 123, // Message id
    "sender_username": "...", // Sender username
    "conversation_id": 123, // Conversation id
    "reply_id": 123, // Optional: Message id
    "content": "...", // Message content
    "sent_at": 123 // Time when message was sent
  }
}
```

Error:

```javascript
{
  "type": "send_message",
  "success": false,
  "error": "..." // Error message
}
```

#### get_messages event

- About:
  - Send user messages of a given conversation.
- Trigger:
  - This event response is sent when an user makes an event request to the server.
- To:
  - This event is sent as a response to the request made by the user.

_EVENT REQUEST_

```javascript
{
  "type": "get_messages",
  "conversation_id": 123, // Conversation id
  "before": 123 // optional: All messages before the given message id
  // if not provided then, it will send the most recent messages
}
```

_EVENT RESPONSE_

Success:

```javascript
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
```

Error:

```javascript
{
  "type": "get_messages",
  "success": false,
  "error": "..." // Error message
}
```
