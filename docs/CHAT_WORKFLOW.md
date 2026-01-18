# Chat Module Workflow Documentation

## Overview

The BizBuch Chat module provides real-time messaging functionality between users using a hybrid approach of REST APIs and WebSockets. This enables both traditional HTTP-based messaging and real-time bidirectional communication.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT APPLICATION                              │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                                    │
                    │ HTTP/REST                          │ WebSocket
                    ▼                                    ▼
┌───────────────────────────────┐       ┌───────────────────────────────────────┐
│        REST API Layer         │       │          WebSocket Layer              │
│  (Django REST Framework)      │       │      (Django Channels)                │
│                               │       │                                       │
│  • ConversationListView       │       │  • ChatConsumer                       │
│  • ConversationDetailView     │       │    - Real-time messaging              │
│  • StartConversationView      │       │    - Typing indicators                │
│  • MessageListView            │       │    - Read receipts                    │
│  • SendMessageView            │       │    - Online/offline status            │
│  • MarkMessagesReadView       │       │                                       │
└───────────────────────────────┘       │  • UserChatConsumer                   │
                    │                   │    - Cross-conversation notifications │
                    │                   └───────────────────────────────────────┘
                    │                                    │
                    ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Database Layer                                  │
│                                                                              │
│  ┌─────────────────────┐            ┌─────────────────────────────────────┐ │
│  │    Conversation     │            │              Message                │ │
│  │                     │ 1      N   │                                     │ │
│  │  • id               │◄──────────►│  • id                               │ │
│  │  • participants     │            │  • conversation (FK)                │ │
│  │  • created_at       │            │  • sender (FK)                      │ │
│  │  • updated_at       │            │  • content                          │ │
│  └─────────────────────┘            │  • timestamp                        │ │
│                                     │  • is_read                          │ │
│                                     │  • read_at                          │ │
│                                     └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### Conversation Model
- **Purpose**: Represents a conversation between two users
- **Key Fields**:
  - `participants`: ManyToMany relation to users
  - `created_at`: Auto timestamp on creation
  - `updated_at`: Auto timestamp on updates (used for ordering)

### Message Model
- **Purpose**: Individual message within a conversation
- **Key Fields**:
  - `conversation`: ForeignKey to Conversation
  - `sender`: ForeignKey to User
  - `content`: Text content of the message
  - `timestamp`: When message was sent
  - `is_read`: Boolean read status
  - `read_at`: When message was read

---

## API Endpoints

### REST API Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/conversations/` | GET | List all user's conversations |
| `/api/chat/conversations/<id>/` | GET | Get conversation details |
| `/api/chat/conversations/start/` | POST | Start/get conversation with user |
| `/api/chat/conversations/<id>/messages/` | GET | Get paginated messages |
| `/api/chat/conversations/<id>/read/` | POST | Mark messages as read |
| `/api/chat/send/` | POST | Send message via REST API |

### WebSocket Routes

| Route | Consumer | Description |
|-------|----------|-------------|
| `ws/chat/<conversation_id>/` | ChatConsumer | Real-time chat in conversation |
| `ws/chat/notifications/` | UserChatConsumer | User-level notifications |

---

## Workflow Diagrams

### 1. Starting a New Conversation

```
User A                          Server                           Database
  │                               │                                  │
  │ POST /conversations/start/    │                                  │
  │ { "user_id": <User B id> }    │                                  │
  │──────────────────────────────►│                                  │
  │                               │   Check existing conversation    │
  │                               │─────────────────────────────────►│
  │                               │◄─────────────────────────────────│
  │                               │                                  │
  │                               │   [If not exists]                │
  │                               │   Create new conversation        │
  │                               │─────────────────────────────────►│
  │                               │◄─────────────────────────────────│
  │                               │                                  │
  │ 201 Created / 200 OK          │                                  │
  │ { conversation details }      │                                  │
  │◄──────────────────────────────│                                  │
```

### 2. Sending a Message (REST API)

```
User A                          Server                     WebSocket Layer
  │                               │                               │
  │ POST /send/                   │                               │
  │ { "recipient_id": X,          │                               │
  │   "content": "Hello!" }       │                               │
  │──────────────────────────────►│                               │
  │                               │                               │
  │                               │ 1. Validate request           │
  │                               │ 2. Get/Create conversation    │
  │                               │ 3. Save message to DB         │
  │                               │                               │
  │                               │   Broadcast to chat room      │
  │                               │──────────────────────────────►│
  │                               │                               │ → User B (if connected)
  │                               │   Notify recipient            │
  │                               │──────────────────────────────►│
  │                               │                               │ → User B's notification channel
  │ 201 Created                   │                               │
  │ { message details }           │                               │
  │◄──────────────────────────────│                               │
```

### 3. Real-time Messaging (WebSocket)

```
User A                    WebSocket Server                    User B
  │                             │                               │
  │ [Connect to WebSocket]      │     [Already Connected]       │
  │ ws://host/ws/chat/1/?token= │                               │
  │────────────────────────────►│                               │
  │                             │                               │
  │ ◄─ Connection Accepted ──── │                               │
  │                             │                               │
  │ [Send Message]              │                               │
  │ { "type": "chat_message",   │                               │
  │   "content": "Hello!" }     │                               │
  │────────────────────────────►│                               │
  │                             │   Save to DB                  │
  │                             │   Broadcast to room           │
  │                             │──────────────────────────────►│
  │                             │                               │
  │ ◄── Message Confirmation ── │ ── New Message ──────────────►│
  │                             │                               │
```

### 4. Typing Indicators

```
User A                    WebSocket Server                    User B
  │                             │                               │
  │ { "type": "typing" }        │                               │
  │────────────────────────────►│                               │
  │                             │   Broadcast typing event      │
  │                             │──────────────────────────────►│
  │                             │                               │
  │                             │     { "type": "typing",       │
  │                             │       "user_id": A,           │
  │                             │       "is_typing": true }     │
  │                             │                               │
  │ { "type": "stop_typing" }   │                               │
  │────────────────────────────►│                               │
  │                             │──────────────────────────────►│
  │                             │     { "type": "typing",       │
  │                             │       "is_typing": false }    │
```

### 5. Read Receipts

```
User B                    WebSocket Server                    User A
  │                             │                               │
  │ { "type": "mark_read",      │                               │
  │   "message_ids": [1,2,3] }  │                               │
  │────────────────────────────►│                               │
  │                             │   Update DB (is_read=true)    │
  │                             │   Broadcast read receipt      │
  │                             │──────────────────────────────►│
  │                             │                               │
  │                             │     { "type": "messages_read",│
  │                             │       "message_ids": [1,2,3], │
  │                             │       "read_by": B }          │
```

### 6. Online/Offline Status

```
User A                    WebSocket Server                    User B
  │                             │                               │
  │ [Connect]                   │                               │
  │────────────────────────────►│                               │
  │                             │   user_online event           │
  │                             │──────────────────────────────►│
  │                             │     { "type": "user_online",  │
  │                             │       "user_id": A }          │
  │                             │                               │
  │ [Disconnect]                │                               │
  │────────────────────────────►│                               │
  │                             │   user_offline event          │
  │                             │──────────────────────────────►│
  │                             │     { "type": "user_offline", │
  │                             │       "user_id": A }          │
```

---

## WebSocket Message Types

### Client → Server Messages

| Type | Payload | Description |
|------|---------|-------------|
| `chat_message` | `{ "content": "string" }` | Send a new message |
| `typing` | `{}` | User started typing |
| `stop_typing` | `{}` | User stopped typing |
| `mark_read` | `{ "message_ids": [int] }` | Mark messages as read |

### Server → Client Messages

| Type | Payload | Description |
|------|---------|-------------|
| `chat_message` | `{ message_id, content, sender_id, sender_username, timestamp }` | New message received |
| `typing` | `{ user_id, username, is_typing }` | Typing indicator |
| `messages_read` | `{ message_ids, read_by, read_at }` | Read receipt |
| `user_online` | `{ user_id, username }` | User came online |
| `user_offline` | `{ user_id, username }` | User went offline |
| `error` | `{ message }` | Error occurred |
| `new_message` | `{ conversation_id, message_id, sender_id, content_preview }` | Notification (UserChatConsumer) |

---

## Authentication

### REST API
- Uses JWT Bearer token in `Authorization` header
- All endpoints require `IsAuthenticated` permission

### WebSocket
- JWT token passed via query string: `ws://host/ws/chat/1/?token=<jwt_token>`
- Or via `Authorization: Bearer <token>` header (if client supports)
- Handled by `JWTAuthMiddleware`

---

## Complete User Journey

### Scenario: User A chats with User B

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: User A opens chat with User B                                          │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  Client                                      Server                            │
│    │                                           │                               │
│    │  POST /conversations/start/               │                               │
│    │  { "user_id": <User B> }                  │                               │
│    │──────────────────────────────────────────►│                               │
│    │                                           │                               │
│    │  { "id": 1, "participants": [...],        │                               │
│    │    "messages": [], ... }                  │                               │
│    │◄──────────────────────────────────────────│                               │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Connect to WebSocket for real-time updates                             │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  Client                                      Server                            │
│    │                                           │                               │
│    │  ws://host/ws/chat/1/?token=<jwt>         │                               │
│    │──────────────────────────────────────────►│                               │
│    │                                           │                               │
│    │  Connection Accepted                      │                               │
│    │◄──────────────────────────────────────────│                               │
│    │                                           │                               │
│    │  Also connect to notifications:           │                               │
│    │  ws://host/ws/chat/notifications/         │                               │
│    │──────────────────────────────────────────►│                               │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Load message history (if needed)                                       │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  Client                                      Server                            │
│    │                                           │                               │
│    │  GET /conversations/1/messages/?page=1    │                               │
│    │──────────────────────────────────────────►│                               │
│    │                                           │                               │
│    │  { "results": [...], "count": 50,         │                               │
│    │    "has_more": true }                     │                               │
│    │◄──────────────────────────────────────────│                               │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Send messages via WebSocket (preferred for real-time)                  │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  User A                      Server                           User B           │
│    │                           │                                │              │
│    │  { "type": "typing" }     │                                │              │
│    │──────────────────────────►│                                │              │
│    │                           │  Typing indicator ────────────►│              │
│    │                           │                                │              │
│    │  { "type": "chat_message",│                                │              │
│    │    "content": "Hi!" }     │                                │              │
│    │──────────────────────────►│                                │              │
│    │                           │  Save to DB                    │              │
│    │                           │  Broadcast to room             │              │
│    │◄─── Message echo ─────────│─── New message ───────────────►│              │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: User B reads the message                                               │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  User B                      Server                           User A           │
│    │                           │                                │              │
│    │  { "type": "mark_read",   │                                │              │
│    │    "message_ids": [1] }   │                                │              │
│    │──────────────────────────►│                                │              │
│    │                           │  Update is_read=true           │              │
│    │                           │  Broadcast read receipt        │              │
│    │                           │─── Read receipt ──────────────►│              │
│    │                           │    { "message_ids": [1],       │              │
│    │                           │      "read_by": B }            │              │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│ ALTERNATIVE: Send messages via REST API                                        │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  User A                      Server                           User B           │
│    │                           │                                │              │
│    │  POST /send/              │                                │              │
│    │  { "recipient_id": B,     │                                │              │
│    │    "content": "Hi!" }     │                                │              │
│    │──────────────────────────►│                                │              │
│    │                           │  Save to DB                    │              │
│    │                           │  WebSocket broadcast           │              │
│    │  201 { message data }     │─── New message (WS) ──────────►│              │
│    │◄──────────────────────────│                                │              │
│                                                                                │
│  Note: REST API also triggers WebSocket notifications, so User B               │
│  receives the message in real-time if connected.                               │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## Error Handling

### REST API Errors
- `400 Bad Request`: Invalid input (missing fields, self-messaging)
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Conversation/User not found or not a participant

### WebSocket Errors
- Connection rejected if user is not authenticated
- Connection rejected if user is not a participant in the conversation
- JSON parse errors return error message type

---

## Best Practices for Client Implementation

1. **Initial Load**:
   - Call `GET /conversations/` to load conversation list
   - Connect to `ws/chat/notifications/` for cross-conversation notifications

2. **Opening a Chat**:
   - Use `POST /conversations/start/` with `user_id` to get/create conversation
   - Connect to `ws/chat/<conversation_id>/` for real-time updates
   - Load recent messages via `GET /conversations/<id>/messages/`

3. **Sending Messages**:
   - Prefer WebSocket for real-time chats (lower latency)
   - Use REST API as fallback when WebSocket unavailable

4. **Message Status**:
   - Track `is_read` status from message data
   - Listen for `messages_read` events for real-time updates

5. **Typing Indicators**:
   - Send `typing` when user starts typing
   - Send `stop_typing` after 2-3 seconds of inactivity
   - Show typing indicator for other users

6. **Pagination**:
   - Load messages in pages (default 50)
   - Use `has_more` to determine if more history exists
   - Implement infinite scroll for older messages

---

## Configuration Requirements

### Django Settings
```python
INSTALLED_APPS = [
    'channels',
    'chat',
    # ...
]

ASGI_APPLICATION = 'mysite.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

### Dependencies
- Django Channels
- channels-redis (for production)
- djangorestframework-simplejwt (for JWT auth)

---

## File Structure

```
chat/
├── __init__.py
├── consumers.py          # WebSocket consumers (ChatConsumer, UserChatConsumer)
├── middleware.py         # JWT authentication for WebSocket
├── routing.py           # WebSocket URL routing
├── urls.py              # REST API URL routing
├── models/
│   ├── __init__.py
│   ├── conversation.py  # Conversation model
│   └── message.py       # Message model
├── serializers/
│   ├── __init__.py
│   ├── conversation_serializer.py
│   └── message_serializer.py
└── views/
    ├── __init__.py
    ├── conversation_views.py  # Conversation REST views
    └── message_views.py       # Message REST views
```

---

## Summary

The chat module provides a robust real-time messaging system with:

- ✅ One-to-one conversations
- ✅ Real-time message delivery via WebSocket
- ✅ REST API fallback for sending messages
- ✅ Typing indicators
- ✅ Read receipts
- ✅ Online/offline presence
- ✅ Message history with pagination
- ✅ JWT authentication for both REST and WebSocket
- ✅ Cross-conversation notifications
