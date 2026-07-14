# Phase 5B — Parent Note Replies & Acknowledgements

Two-way **note threads** (not a general chat). Each `StudentParentNote` is the root message; replies stay under that note.

## Database changes

**Migration:** `0014_parent_note_threads.py`

### Extended: `student_parent_notes`

| Column | Type | Description |
|--------|------|-------------|
| `status` | enum string | `new`, `read`, `replied`, `closed` |
| `priority` | enum string | `low`, `medium`, `high`, `urgent` |
| `closed_at` | timestamptz nullable | Teacher closed discussion |
| `closed_by_user_id` | FK users nullable | Who closed |

### Existing: `student_parent_note_reads`

Per-parent acknowledgement (unchanged):

- `parent_id`, `read_at` — supports multiple linked parents

### New: `student_parent_note_replies`

| Column | Description |
|--------|-------------|
| `id` | PK |
| `note_id` | FK → note |
| `author_id` | FK → users |
| `author_role` | `teacher` \| `parent` |
| `body` | Text |
| `created_at`, `updated_at` | Timestamps |

## Status rules

| Status | Condition |
|--------|-----------|
| **new** | No parent read, no replies |
| **read** | At least one parent read record, no replies |
| **replied** | At least one reply (auto-updated on reply) |
| **closed** | Teacher closed (`closed_at` set); no new replies |

Closed overrides other states for display and `can_reply`.

## Priority (teacher)

| Value | UI color |
|-------|----------|
| low | grey (neutral) |
| medium | blue (info) |
| high | orange (warning) |
| urgent | red (error) |

## APIs

### Parent (`/parent`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notes` | List notes (status, priority, `reply_count`) |
| GET | `/notes/unread-count` | Unread counter |
| GET | `/notes/{note_id}` | Full thread with replies |
| POST | `/notes/{note_id}/acknowledge` | Mark read (✓ تمت القراءة) |
| POST | `/notes/{note_id}/read` | Alias for acknowledge |
| POST | `/notes/{note_id}/reply` | Parent reply |
| PATCH | `/notes/{note_id}/replies/{reply_id}` | Edit **own** reply |
| DELETE | `/notes/{note_id}/replies/{reply_id}` | Delete **own** reply |

### Teacher (`/teacher/students`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/{student_id}/parent-notes` | List with metadata |
| GET | `/{student_id}/parent-notes/{note_id}` | Full thread |
| POST | `/{student_id}/parent-notes` | Create (optional `priority`) |
| PATCH | `/{student_id}/parent-notes/{note_id}` | Update note |
| DELETE | `/{student_id}/parent-notes/{note_id}` | Delete note |
| POST | `/{student_id}/parent-notes/{note_id}/close` | Close thread |
| POST | `/{student_id}/parent-notes/{note_id}/reply` | Teacher reply |
| PATCH | `/{student_id}/parent-notes/{note_id}/replies/{reply_id}` | Edit **own** reply |
| DELETE | `/{student_id}/parent-notes/{note_id}/replies/{reply_id}` | Delete **own** reply |
| GET | `/parent-notes/priorities` | Priority options |
| GET | `/parent-notes/statuses` | Status options |

## Authorization

- **Parent:** Must be linked to note’s `student_id` (`resolve_parent_student_id`).
- **Teacher:** Must have student in scope (`assert_student_in_teacher_scope`); only note author can edit/delete/close the **note**.
- **Replies:** `can_edit` / `can_delete` only when `reply.author_id === viewer.id`.

## Notifications

| Event | Recipient | Type | Body (EN) |
|-------|-----------|------|-----------|
| Teacher creates note | Linked parents | `parent_note` | New note from your teacher. |
| Parent acknowledges | Note’s teacher | `parent_note_read` | (Arabic summary with parent name) |
| Parent replies | Note’s teacher | `parent_note_reply` | Parent replied to your note. |
| Teacher replies | Linked parents | `parent_note_reply` | Your teacher replied to a note. |

## Files modified

### Backend

- `backend/app/models/student_parent_note.py` — enums, replies model
- `backend/app/models/notification.py` — `parent_note_reply`
- `backend/app/models/__init__.py`
- `backend/app/schemas/parent_notes.py` — replies, status, priority
- `backend/app/services/parent_note_service.py` — thread logic
- `backend/app/api/parent.py` — parent routes
- `backend/app/api/teacher_students.py` — teacher routes
- `backend/alembic/versions/0014_parent_note_threads.py`

### Frontend

- `src/api/parentNotes.js`
- `src/constants/parentNoteMeta.js`
- `src/components/parent/ParentNoteThread.vue` — threaded RTL UI
- `src/components/parent/ParentNoteCard.vue` — clamp prop
- `src/components/parent/ParentNotesSection.vue`
- `src/components/teacher/TeacherParentNotesSection.vue`

## Workflows

### Teacher

1. Student profile → **ملاحظات أولياء الأمور** → create note (category + **priority**).
2. List shows **status**, **priority**, **reply count**, read summary.
3. **عرض المحادثة** → full thread; reply, edit/delete own replies, **إغلاق المحادثة**.

### Parent

1. Dashboard → **ملاحظات المعلّم** + **unread** badge.
2. **تمت القراءة** → acknowledge + teacher notified.
3. Expand thread → reply; edit/delete own replies only.

## Screenshots (manual QA)

Capture in browser after `alembic upgrade head` and refresh dev app:

1. Teacher: new note with urgent priority  
2. Parent: unread → acknowledge  
3. Parent reply → teacher notification  
4. Teacher reply → parent notification  
5. Closed thread — reply box hidden  

Reference layout: `docs/parent-notes-visual-verification.html` (Phase 5A contrast); threads use `ParentNoteThread.vue` styles.

## Deploy

```bash
cd backend && alembic upgrade head
```

Restart API + frontend dev server.

## Not in scope

- General messaging / DMs  
- Admin moderation UI  
- Email/SMS for note replies (in-app notifications only)
