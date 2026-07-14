# Quiz System Hardening Report (Phase 1)

## Root causes found

| Issue | Root cause |
|-------|------------|
| Timer stuck at 59:59 | `time_remaining_seconds` was rendered once from the API with **no client-side countdown** (`setInterval`). A 60-minute quiz correctly shows 59:59 immediately after start but never ticked down. |
| Past due dates allowed | Backend `create_quiz` / `update_quiz` accepted any `due_at` with no future-date check. |
| Question edit missing | `PUT .../questions/{id}` existed and `updateManualQuestion` was in the API client, but **TeacherQuizBuilderView never wired edit UI**. |
| Update question validation gap | `update_question` did not re-run `_validate_question_payload` after merges. |
| Total marks not shown | `CourseQuizOut` had no `total_points`; UI never summed question points. |
| Glass-card transparency | Quiz builder and question dialog used `glass-card` styling with low opacity, hurting readability. |
| Student results layout | Score shown as secondary text; percentage and `score / max_score` were not prominent. |

Scoring logic (`_recalculate_attempt`) was already correct: `max_score` = sum of question points, `percent` = `score / max_score * 100`.

---

## Files modified

### Backend
- `backend/app/schemas/course_quiz.py` — `total_points` on quiz outputs; `score`/`max_score` on student list items
- `backend/app/services/course_quiz_service.py` — due-date validation, total points helpers, timer helpers, time enforcement on answer save, question update validation

### Frontend
- `src/views/teacher/TeacherQuizBuilderView.vue` — UX overhaul, edit questions, validation, total marks
- `src/views/student/StudentManualQuizView.vue` — live countdown, auto-submit, results display, total marks
- `src/views/teacher/TeacherQuizzesView.vue` — total points in list
- `src/views/teacher/TeacherQuizResultsView.vue` — quiz total in results header
- `src/components/student/CourseQuizzesPanel.vue` — total points + student score summary

---

## Validation verification

| Rule | Frontend | Backend |
|------|----------|---------|
| Due date must be in future | `datetime-local` `min` + `validateDueAt()` before save | `_validate_due_at()` on create/update when `due_at` set |
| Passing score 0–100 | Input min/max | HTTP 400 if out of range |
| Duration ≥ 1 minute | Input min | HTTP 400 if &lt; 1 |
| Question text required | Dialog validation | Existing + update re-validation |
| MCQ ≥ 2 options | Dialog validation | `_validate_question_payload` |
| Short answer model required | Dialog validation | `_validate_question_payload` |

Error messages (Arabic): e.g. `موعد التسليم يجب أن يكون في المستقبل`, `انتهى وقت الكويز — يرجى تسليم الإجابات`.

---

## Timer verification

| Scenario | Expected behavior |
|----------|-------------------|
| Start 60-min quiz | Shows ~59:59, decrements every second |
| After 5 seconds | Shows ~59:54 |
| Page refresh (in progress) | Re-fetches `time_remaining_seconds` from server and restarts countdown |
| Tab refocus | `visibilitychange` triggers server sync |
| Timer reaches 0 | Auto-submits attempt |
| Save after expiry | Backend rejects with 400; UI shows error |

Implementation: `startCountdown()` with `setInterval(1000)`; `_time_remaining_seconds()` on server uses UTC-normalized `started_at`.

---

## Total marks & results verification

| Location | Display |
|----------|---------|
| Teacher builder | Chip + questions section: **إجمالي الدرجات: N** |
| Teacher quiz list | `N نقطة` per quiz |
| Teacher results | Header: total quiz points |
| Student pre-start | **إجمالي الدرجات: N نقطة** |
| Student post-submit | **18 / 20** (large) + **90%** |
| Course quiz panel | Total points + **score / max_score (percent%)** when graded |

Example after submission:
```
18 / 20
90%
```

---

## Build verification

Run: `npm run build` — should pass with no Vite import errors.

---

## Out of scope (unchanged)

- AI lesson quizzes (`StudentLessonView`, `QuizResults.vue`) — separate system, count-based not points-based
- Question reorder UI
- Clearing `due_at` to null on backend update (pre-existing limitation)
