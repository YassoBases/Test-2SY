# Phase 8 — Gamification Foundation

Foundation-only: XP, levels, achievements, streaks. No rewards store, coupons, or AI credits.

---

## Database schema

### Migration `0022_gamification_foundation.py`

**`student_xp`**
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| student_id | FK users, unique | One row per student |
| total_xp | int | Default 0 |
| level | int | Cached 1–10 |
| awarded_keys_json | text | Idempotency keys JSON array |
| updated_at | timestamptz | |

**`student_achievements`**
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| student_id | FK users | |
| achievement_key | string | Unique per student |
| icon | string | e.g. 🎓 |
| title | string | Arabic title |
| description | text | |
| unlocked_at | timestamptz | |

Run: `cd backend && alembic upgrade head`

---

## XP service

| File | Role |
|------|------|
| `services/gamification/xp_levels.py` | `xp_to_level()`, `level_progress()`, thresholds L1–L10 |
| `services/gamification/xp_service.py` | Idempotent `award_xp()`, event handlers, profile |
| `services/gamification/achievement_service.py` | Registry + unlock checks |

### XP awards (automatic only)

| Action | XP | Idempotency key |
|--------|-----|-----------------|
| Complete lesson | 20 | `lesson:{id}` |
| Long lesson | 35 | same |
| Module (5-lesson batch) | 100 | `module:{course}:{batch}` |
| Complete course | 500 | `course:{id}` |
| Complete quiz | 30 | `lesson_quiz:{id}` / `manual_quiz:{id}` |
| Quiz 80%+ / 90%+ / 100% | 20 / 40 / 75 | tier bonus keys |
| Planner task | 15 | `planner_task:{id}` |
| All tasks today | 75 | `planner_day:{date}` |
| Weekly plan done | 250 | `planner_week:{iso}` |
| Study day | 10 | `study_day:{date}` |
| Streak 7 / 14 / 30 | 100 / 250 / 750 | `streak_milestone:{n}` |

**Not awarded:** login, page views, messages, notifications.

### Integration hooks (`integration_hooks.py`)

- `after_lesson_completed` → lesson + course/module XP + streak
- `after_lesson_quiz_submitted` → quiz XP + streak
- `after_quiz_submitted` → manual quiz XP + streak
- `after_planner_task_completed` → planner XP + streak

---

## Achievements

| Key | Icon | Trigger |
|-----|------|---------|
| first_course_completed | 🎓 | First course 100% |
| first_perfect_quiz | 🧠 | First 100% quiz |
| streak_7 | 🔥 | 7-day streak |
| streak_30 | ⚡ | 30-day streak |
| lessons_100 | 📚 | 100 lessons completed |
| excellent_quizzes_10 | 🏆 | 10 quizzes ≥ 80% |

---

## APIs

| Method | Path | Audience |
|--------|------|----------|
| GET | `/student/gamification` | Student profile |
| GET | `/student/dashboard` | Includes `gamification` |
| GET | `/parent/dashboard` | Includes `gamification` (read-only) |
| GET | `/teacher/students/{id}` | Includes `gamification` (read-only) |

---

## Frontend

| Component | Use |
|-----------|-----|
| `GamificationCard.vue` | Student dashboard — level, XP bar, streak |
| `GamificationPanel.vue` | Parent + teacher read-only |
| `src/api/gamification.js` | API client |

---

## Screenshots to capture

1. Student **دوراتي** — gamification card (Level, XP, streak)
2. Complete lesson/quiz — XP increases on refresh
3. Parent dashboard — التقدّم والإنجازات section
4. Teacher student profile — XP والإنجازات section
5. Unlocked achievement chip after milestone

---

## Build

```bash
npm run build
```
