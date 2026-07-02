# Phase 4 — Teacher Student Management & Monitoring

## Summary

Teachers now have a dedicated student directory with instant search, detailed per-student profiles (learning progress, quiz analytics, language module, activity timeline), and private teacher notes. All data is scoped to students with paid access on the teacher's courses.

---

## Database changes

### New table: `teacher_student_notes`

| Column | Type | Notes |
|--------|------|-------|
| `id` | serial PK | |
| `teacher_profile_id` | FK → `teacher_profiles.id` | CASCADE delete |
| `student_id` | FK → `users.id` | CASCADE delete |
| `note_text` | text | 1–2000 chars (validated in API) |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Migration:** `backend/alembic/versions/0012_teacher_student_notes.py`

Run:

```bash
cd backend
alembic upgrade head
```

**No changes** to existing tables. Reads from: `users`, `student_profiles`, `student_course_access`, `courses`, `lessons`, `student_lesson_progress`, `quiz_attempts`, `course_quiz_attempts`, `student_activity_events`, `language_analytics`, `language_activity_log`, `language_certificates`, `language_subscriptions`, `auth_sessions`.

---

## APIs created

Prefix: `/api/teacher/students` (requires `teacher` role)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/teacher/students` | Search directory (`q`, `grade`, `subject_id`) |
| `GET` | `/teacher/students/{student_id}` | Full profile + analytics + notes |
| `GET` | `/teacher/students/{student_id}/notes` | List notes |
| `POST` | `/teacher/students/{student_id}/notes` | Create note |
| `PATCH` | `/teacher/students/{student_id}/notes/{note_id}` | Edit note |
| `DELETE` | `/teacher/students/{student_id}/notes/{note_id}` | Delete note |

---

## Authorization verification

1. **Role gate:** All routes use `require_role(UserRole.teacher)`.
2. **Student scope:** `assert_student_in_teacher_scope()` requires a `student_course_access` row with `payment_status = paid` on at least one course owned by the teacher (`course.teacher_profile_id`).
3. **Notes isolation:** Notes are filtered by `teacher_profile_id` — teachers only see/edit their own notes; students and parents have no API access.
4. **404 not 403:** Out-of-scope student IDs return `404` with Arabic message `الطالب غير موجود` to avoid leaking enrollment data.

---

## Search performance notes

| Aspect | Implementation |
|--------|----------------|
| **Before** | Frontend N+1: `fetchTeacherGrades()` + one `fetchTeacherCourseDetail()` per course |
| **After** | Single `GET /teacher/students` with server-side join on paid access |
| **Filters** | `ILIKE` partial match on name/email; optional grade/subject narrow course set first |
| **Dedup** | One row per student (aggregated across teacher courses) |
| **Debounce** | Frontend 300 ms debounce on search/filter changes |
| **Profile cost** | Profile endpoint runs richer aggregations; acceptable for single-student drill-down |

For teachers with 50+ students, consider caching course lesson IDs per teacher session or materialized rollups (`student_analytics` table already exists for future optimization).

---

## Files modified / created

### Backend

| File | Change |
|------|--------|
| `backend/app/models/teacher_student_note.py` | **New** model |
| `backend/app/models/__init__.py` | Export `TeacherStudentNote` |
| `backend/alembic/versions/0012_teacher_student_notes.py` | **New** migration |
| `backend/app/schemas/teacher_students.py` | **New** Pydantic schemas |
| `backend/app/services/teacher_student_service.py` | **New** search, profile, notes logic |
| `backend/app/api/teacher_students.py` | **New** router |
| `backend/app/api/router.py` | Register `teacher_students` router |

### Frontend

| File | Change |
|------|--------|
| `src/api/teacherStudents.js` | **New** API client |
| `src/views/teacher/TeacherStudentsView.vue` | Search + table directory |
| `src/views/teacher/TeacherStudentProfileView.vue` | **New** full profile page |
| `src/router/index.js` | Route `/teacher/students/:studentId` |
| `src/constants/app.js` | `TEACHER_STUDENTS`, `TEACHER_STUDENT_PROFILE` |

---

## UI features delivered

### Student directory (`/teacher/students`)

- Instant search (name, email) with 300 ms debounce
- Filters: grade, subject (optional)
- Table: avatar, name, email, grade, active status, last activity, completion %, avg quiz %
- Loading, error, and empty states
- **View Profile** action → `/teacher/students/:studentId`

### Student profile

- **Info:** name, email, grade, registration, last login, account status
- **Analytics cards:** completion %, avg score, study activity, streak, last active
- **Learning:** enrolled subjects, subscriptions, course progress table
- **Quiz analytics:** totals, avg/best/lowest, recent attempts table
- **Language:** CEFR levels, vocabulary/writing/speaking progress, certificates
- **Activity timeline:** lessons, quizzes, writing/speaking, certificates
- **Teacher notes:** add, edit, delete (private)

---

## Test scenarios

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Teacher opens `/teacher/students` | Paid subscribers listed; empty state if none |
| 2 | Type partial name in search | Results filter instantly (debounced) |
| 3 | Filter grade 10 + subject Physics | Only matching enrolled students |
| 4 | Click **View Profile** | Profile loads with all sections |
| 5 | Teacher A requests Teacher B's student ID | `404` |
| 6 | Add note "Needs support in Mathematics" | Appears in notes list |
| 7 | Edit / delete note | Updates persist; only owning teacher sees notes |
| 8 | Student with language progress | CEFR levels and progress bars shown |
| 9 | Student with quiz attempts | History table with scores and dates |
| 10 | `npm run build` | Passes ✓ |
| 11 | Backend import `teacher_student_service` | Passes ✓ |

---

## Screenshots

UI mockups (RTL dark glass-card theme) are in the Cursor project `assets/` folder:

- `phase4-teacher-students-directory.png` — search bar, filters, student table
- `phase4-teacher-student-profile.png` — summary cards, quiz table, timeline, notes

> Live QA: log in as teacher, navigate to **الطلاب**, open any student profile after running migration.

---

## Manual QA checklist

1. Run `alembic upgrade head` on your database (**required** for `teacher_student_notes`)
2. Restart backend (`uvicorn app.main:app --reload --port 8000`)
3. Hard-refresh frontend (`npm run dev`)
4. Verify search, profile, notes CRUD, and out-of-scope 404

---

## Bug fix (2026-06-04): Profile 500 Internal Server Error

### Traceback

```
File teacher_student_service.py, line 540, in _build_language_summary
    vocabulary_progress_percent=int(growth.get("vocabulary") or 0),
TypeError: int() argument must be a string, a bytes-like object or a real number, not 'dict'
```

Secondary error after partial failure (if migration not applied):

```
asyncpg.exceptions.UndefinedTableError: relation "teacher_student_notes" does not exist
```

### Root cause

1. **Primary:** `skill_growth_json["vocabulary"]` (and `"writing"` / `"speaking"`) are **nested dicts** with a `growth_percent` field — not integers. Calling `int(growth.get("vocabulary"))` raised `TypeError`.
2. **Secondary:** Migration `0012_teacher_student_notes` was not applied, so notes query failed after language block was reached.

### Fix

- Added `_skill_growth_percent()` helper to safely read `growth_percent` from nested skill dicts or top-level `*_completion_percent` keys.
- Run `alembic upgrade head` to create `teacher_student_notes`.

### Verification (local)

| Student | Activity | Language | Result |
|---------|----------|----------|--------|
| #15 (fayez) | none | yes (0% vocab) | OK |
| #9 (omar) | none | yes (0% vocab) | OK |
| #12 | none | yes | OK |
