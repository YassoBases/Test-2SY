# Phase 6B — Smart Messaging & Attachments

Teacher communication workspace built on Phase 6A internal messaging.

## Requirements coverage

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Conversation header: avatar, name, grade, status + quick actions | Done |
| 2 | Student context card (teacher only) | Done |
| 3 | File attachments: upload, download, preview | Done |
| 4 | Voice: record, preview before send, playback after | Done |
| 5 | Pin, archive, mark unread, search, delete own message | Done |
| 6 | Parent context: name, linked student, grade | Done |
| 7 | Group participant list (teacher, student, parent) | Done |
| 8 | Notifications: sender, preview, conversation link | Done |
| 9 | UI: bubbles, avatars, badges, hover, empty states | Done |

## Database (`0016_smart_messaging`)

```bash
cd backend && alembic upgrade head
```

### `conversation_participants`

- `is_pinned` (boolean)
- `is_archived` (boolean)

### `conversation_messages`

- `message_kind` — `text` \| `image` \| `pdf` \| `document` \| `voice`
- `attachment_url`, `attachment_name`, `attachment_mime`
- `voice_duration_ms`
- `deleted_at` (soft delete)

## APIs (`/api/messages`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/conversations?include_archived=` | List (pinned first) |
| GET | `/conversations/{id}` | Thread + messages |
| GET | `/conversations/{id}/context` | Student/parent context (teacher) |
| GET | `/conversations/{id}/messages/search?q=` | Search in thread |
| PATCH | `/conversations/{id}/settings` | Pin / archive |
| POST | `/conversations/{id}/mark-unread` | Mark unread |
| PATCH | `/conversations/{id}/participants` | Group: add/remove parent, add student |
| POST | `/conversations/{id}/messages` | Text message |
| POST | `/conversations/{id}/messages/attachment` | Multipart file (+ caption, voice_duration_ms) |
| DELETE | `/messages/{message_id}` | Delete own message |

## Attachment support

- **Storage:** `uploads/messages/thread_{id}/`
- **Types:** images (15 MB), PDF/docs (15 MB), voice WebM/MP3/OGG/WAV (8 MB)
- **UI:** preview before send; in-thread preview dialog (image/PDF); download links

## Voice support

- Browser `MediaRecorder` → WebM file
- Preview `<audio>` before send
- Playback `<audio controls>` in `MessageBubble`

## Student context integration

`messaging_context_service.get_thread_context` aggregates:

- `teacher_student_service` — completion %, quiz average, streak, subjects, last activity
- `parent_note_service` — latest parent interaction in snapshot
- Profile activity timeline — latest lesson

## Files modified / added

### Backend

- `alembic/versions/0016_smart_messaging.py`
- `app/models/conversation.py`
- `app/schemas/messaging.py`
- `app/services/messaging_service.py`
- `app/services/messaging_media_service.py`
- `app/services/messaging_context_service.py`
- `app/api/messages.py`

### Frontend

- `src/api/messages.js`
- `src/views/messages/MessagesView.vue`
- `src/components/messages/ConversationThreadHeader.vue`
- `src/components/messages/StudentContextPanel.vue`
- `src/components/messages/MessageComposer.vue`
- `src/components/messages/MessageBubble.vue`
- `src/components/messages/ParticipantListBar.vue`
- `src/components/messages/GroupParticipantsManager.vue`
- `src/components/messages/SnapshotRow.vue`
- `src/components/layout/NotificationBell.vue`

## Screenshots (capture locally)

1. **Teacher header** — avatar, name, grade, active chip, four quick-action buttons  
2. **Context card** — completion, quiz avg, streak, last activity, subjects  
3. **Attachment** — preview card before send + image/PDF in thread with download  
4. **Voice** — record preview + sent audio player  
5. **Group** — participant bar with معلّم / طالب / ولي أمر badges  
6. **Notification** — `رسالة جديدة` + `الاسم: مقتطف الرسالة` → opens thread  

## Deploy

1. `alembic upgrade head`
2. Restart API server
3. Hard-refresh frontend (`npm run dev` or production build)
