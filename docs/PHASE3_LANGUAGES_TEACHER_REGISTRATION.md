# Phase 3 — Languages & Teacher Registration Report

## Summary

Hardened language module validation (writing, speaking, vocabulary, placement) and teacher grade/subject registration with tiered subject catalogs and server-side enforcement.

---

## 1. Writing validation

### Behavior
- Submissions **below the prompt's `min_words`** are **rejected** before scoring.
- Error message: **`Minimum {N} words required.`** (e.g. `Minimum 80 words required.` for 80-word prompts).
- Sentence minimum also enforced when `min_sentences` is set on the prompt.

### Frontend
- `StudentLanguageWritingView.vue` — live word/sentence counts, inline warning, disabled submit until valid.
- `StudentLanguagePlacementView.vue` — validates writing answers before next/submit.
- Shared helper: `src/utils/languageValidation.js`

### Backend
- `language_validation.py` — `validate_writing_submission()`, `min_words_required_message()`
- `language_writing_service.py` — rejects short text at `POST .../writing/{id}/submit`
- `language_placement_service.py` — validates all writing responses on placement submit

---

## 2. Language module audit fixes

| Module | Issue | Fix |
|--------|-------|-----|
| **Writing** | Short text accepted, failed only on pass score | Hard reject below `min_words` (FE + BE) |
| **Writing** | FE sentence count differed from BE | Both use split-on-punctuation logic via shared helpers |
| **Speaking** | Pass without meeting `min_seconds` | `validate_speaking_duration()` required on submit (FE + BE) |
| **Speaking** | Upload alone could pass | Pass now requires duration ≥ `min_seconds` |
| **Vocabulary** | Free-form `action` string in schema | `VocabularyReviewIn.action: Literal["known", "review_later"]` |
| **Placement** | Writing/speaking mins advisory only | Enforced on final placement submit |
| **Certificates** | No input validation needed | Read-only; eligibility unchanged (analytics CEFR levels) |

---

## 3. Teacher registration — grade-based subjects

### Tiered catalog (`reference_catalog.py`)

| Grade tier | Grades | Subjects |
|------------|--------|----------|
| Elementary | 1–6 | رياضيات، علوم، عربي، إنكليزي |
| Middle | 7–9 | Above + فيزياء، كيمياء |
| Secondary | 10–12 | رياضيات، عربي، إنكليزي، فيزياء، كيمياء، أحياء |

Examples:
- **Grade 4** → Mathematics, Science, Arabic, English
- **Grade 10** → Physics, Chemistry, Biology (+ Math, Arabic, English)

### Frontend
- `TeacherSetupView.vue` — subjects grouped by grade; list refreshes when grades change; stale subject picks pruned.
- `TeacherProfileView.vue` — same pruning when grades change.

### Backend
- `GET /teacher/setup/subjects?grade=` — ensures reference rows, returns only tier-allowed active subjects.
- `PUT /teacher/setup/teaching` — validates every `subject_id` belongs to a selected grade and is allowed for that grade tier.

---

## 4. Database impact

| Area | Impact |
|------|--------|
| `subjects` | `ensure_reference_subjects()` syncs `is_active` per grade tier; adds **biology** slug for secondary; deactivates out-of-tier rows |
| `teacher_profile_subjects` | No schema change; invalid combinations rejected on save |
| `teacher_profile_grades` | No schema change |
| Language tables | **No migration** — validation is application-layer |

**Ops note:** Run backend once (or hit `/teacher/setup/subjects?grade=N` for each grade) to sync subject `is_active` flags on existing databases.

---

## 5. APIs modified

| Method | Path | Change |
|--------|------|--------|
| POST | `/student/languages/writing/{id}/submit` | 400 if below `min_words` |
| POST | `/student/languages/speaking/{id}/submit` | 400 if below `min_seconds` |
| POST | `/student/languages/placement/.../submit` | Writing/speaking mins enforced |
| GET | `/teacher/setup/subjects` | Tier-filtered subjects + `slug` in response |
| PUT | `/teacher/setup/teaching` | Grade/subject combination validation |

---

## Files modified

### Backend
- `backend/app/services/language_validation.py` *(new)*
- `backend/app/services/language_writing_service.py`
- `backend/app/services/language_speaking_service.py`
- `backend/app/services/language_placement_service.py`
- `backend/app/schemas/language_learning.py`
- `backend/app/core/reference_catalog.py`
- `backend/app/services/teacher_setup_service.py`
- `backend/app/api/teacher_setup.py`

### Frontend
- `src/utils/languageValidation.js` *(new)*
- `src/views/student/languages/StudentLanguageWritingView.vue`
- `src/views/student/languages/StudentLanguageSpeakingView.vue`
- `src/views/student/languages/StudentLanguagePlacementView.vue`
- `src/views/teacher/TeacherSetupView.vue`
- `src/views/teacher/TeacherProfileView.vue`

---

## Verification checklist

### Writing
1. Open a B1 prompt with `min_words: 80`
2. Submit 50 words → UI blocks + shows `Minimum 80 words required.`
3. API returns 400 with same message
4. Submit 80+ words → accepted and scored

### Speaking
1. Record & upload < 20s (or prompt min)
2. Submit disabled / API 400 `Minimum N seconds required.`

### Teacher setup
1. Select grade 4 → see Math, Science, Arabic, English only
2. Select grade 10 → see Physics, Chemistry, Biology (+ core subjects)
3. Deselect grade → subjects for that grade removed from selection
4. Save invalid subject/grade combo via API → 400 rejected
