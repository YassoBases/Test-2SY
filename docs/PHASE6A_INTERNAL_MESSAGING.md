# Phase 6A — Internal Messaging System

In-platform messaging for teachers, students, and parents. Not WhatsApp; no attachments, voice, WebSockets, or AI in this phase.

## Database (`0015_internal_messaging`)

### `conversation_threads`

| Column | Description |
|--------|-------------|
| id | PK |
| title | Display title (auto or custom) |
| thread_type | `teacher_student`, `teacher_parent`, `teacher_student_parent` |
| student_id | Anchor student (permissions) |
| created_by_user_id | Usually teacher |
| last_message_at, last_message_preview | List sorting |
| created_at, updated_at | |

### `conversation_participants`

| Column | Description |
|--------|-------------|
| thread_id, user_id | Unique pair |
| role | teacher / student / parent |
| last_read_at | Unread calculation |

### `conversation_messages`

| Column | Description |
|--------|-------------|
| thread_id, sender_id, body | Message content |
| status | `sent`, `delivered`, `read` (sender aggregate) |
| created_at | |

### `conversation_message_reads`

Per-recipient read receipts (`message_id`, `user_id`, `read_at`).

## APIs (`/messages`)

| Method | Path | Who |
|--------|------|-----|
| GET | `/conversations` | Participant |
| GET | `/conversations/unread-count` | Participant |
| GET | `/conversations/{id}?mark_read=` | Participant |
| POST | `/conversations` | **Teacher only** |
| GET | `/contacts` | Teacher (create dialog) |
| POST | `/conversations/{id}/messages` | Participant |
| POST | `/conversations/{id}/read` | Participant |
| POST | `/messages/{message_id}/read` | Participant |

## Authorization

| Role | Rule |
|------|------|
| Teacher | Create threads; participants must be in-scope students + linked parents |
| Student | Only threads where `student_id = self` and user is participant |
| Parent | Only threads where `student_id` is a linked child and user is participant |
| Replies | Cannot edit others’ messages (N/A — no edit in 6A) |

## Read status

- On send: `delivered` when message is stored; recipients get in-app notification.
- On open thread (`mark_read=true`) or `/read`: receipts + `last_read_at`.
- Sender UI: **أُرسلت** / **وُصلت** / **قُرئت** when all other participants read.

## Notifications

- Type: `internal_message`
- Title: رسالة جديدة
- Body: `New message from {sender}.`
- Payload: `thread_id`, `message_id`

## Frontend

| Path | Role |
|------|------|
| `/teacher/messages` | Teacher (+ new conversation) |
| `/student/messages` | Student |
| `/parent/messages` | Parent |

- RTL split layout: conversation list (right in RTL) + thread
- Polling every 12s (no WebSocket)
- Nav item **الرسائل** on all three sidebars

## Files

**Backend:** `models/conversation.py`, `schemas/messaging.py`, `services/messaging_service.py`, `api/messages.py`, `alembic/versions/0015_internal_messaging.py`

**Frontend:** `api/messages.js`, `views/messages/MessagesView.vue`, `components/messages/NewConversationDialog.vue`, `config/navigation.js`, `router/index.js`

## Deploy

```bash
cd backend && alembic upgrade head
```

Restart API server.

## Workflows

1. **Teacher:** الرسائل → محادثة جديدة → pick student, optional parents → send messages.
2. **Student:** الرسائل → open thread started by teacher → reply.
3. **Parent:** Same as student for threads they’re in.

## Out of scope (Phase 6A)

- WebSockets / live typing
- File & voice attachments
- Message edit/delete
- WhatsApp bridge
