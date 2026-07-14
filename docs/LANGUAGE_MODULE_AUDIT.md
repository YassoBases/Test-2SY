# Language Module Audit

**Date:** 2026-06-02  
**Scope:** Phases A → C2 (subscription, placement, reading, listening, vocabulary, writing, speaking, progress, parent API readiness)  
**Method:** Static code review, DB schema audit, service-layer smoke tests (`backend/scripts/audit_language_services.py`), partial HTTP verification via FastAPI TestClient, frontend route/view inventory.

---

## Executive Summary

The Language Module is **functionally complete** for student learning flows (Phases A–C2). All 9 frontend views exist, 25 backend routes load without import errors, and seeded content (30 reading/listening lessons, 60 vocabulary cards, 15 writing + 15 speaking prompts) is present at migration `0011_language_c2`.

**Production readiness: Conditional Go** — suitable for staged rollout with known limitations below. Blockers for full production confidence: parent UI not wired, router guard gaps, no automated E2E test suite, and empty progress tables in dev (no student activity recorded yet).

---

## 1. Route & Page Inventory

| Route | View | Status |
|-------|------|--------|
| `/student/languages` | `StudentLanguagesHubView.vue` | OK |
| `/student/languages/subscribe` | `StudentLanguageSubscribeView.vue` | OK |
| `/student/languages/placement` | `StudentLanguagePlacementView.vue` | OK (results deep-link fixed) |
| `/student/languages/reading` | `StudentLanguageReadingView.vue` | OK |
| `/student/languages/listening` | `StudentLanguageListeningView.vue` | OK |
| `/student/languages/vocabulary` | `StudentLanguageVocabularyView.vue` | OK |
| `/student/languages/writing` | `StudentLanguageWritingView.vue` | OK |
| `/student/languages/speaking` | `StudentLanguageSpeakingView.vue` | OK |
| `/student/languages/progress` | `StudentLanguageProgressView.vue` | OK |

**Tabs:** `LanguageModuleTabs.vue` covers all 7 learning modules (shown when subscribed + placement complete).

**Empty states:** All skill views now show Arabic empty-state messages when no content is available. Writing/Speaking also show “select a prompt” placeholder.

---

## 2. API Endpoint Audit

**Router:** `backend/app/api/language_student.py` — 25 routes under `/api/student/languages`.

| Endpoint group | Count | Auth guard | Verified |
|----------------|-------|------------|----------|
| Access / product / subscribe | 3 | student / none | Service + TestClient (access 200) |
| Placement | 5 | active subscription | Code review |
| Hub / progress | 2 | learning ready | Service layer |
| Reading / listening | 6 | learning ready | Service layer (student 5 & 47) |
| Vocabulary | 3 | learning ready | Service layer (20 cards/student) |
| Writing / speaking | 8 | learning ready | Service layer (5 prompts/skill/level) |

**Import fix applied:** `WritingPromptOut` and `SpeakingPromptOut` were missing from `language_student.py` imports — caused router load failure at startup.

**No broken endpoints found** in service-layer testing. HTTP batch testing via TestClient hit async event-loop limits on Windows when running many sequential requests; live uvicorn testing confirmed `/progress` returns 200 for active students.

---

## 3. Button & Action Audit

| View | Actions | Notes |
|------|---------|-------|
| Hub | Subscribe, placement, results, retake, 6 skill links | OK |
| Subscribe | Subscribe via paywall card | OK |
| Placement | MCQ autosave, writing autosave, record/stop, prev/next, submit, journey/hub | Results via `?results=1` fixed |
| Reading / Listening | Select lesson, submit MCQ, retry | Redirect on access gate fixed |
| Vocabulary | Reveal, Known, Review Later, prev/next | OK |
| Writing | Select prompt, submit text | Error handling + redirect fixed |
| Speaking | Select, record/stop, upload, submit | Error handling + redirect fixed |
| Progress | Read-only dashboard | OK |

---

## 4. Progress Dashboard vs Database

**Test students:** `test.student@example.com` (id=5, reading C1→content fallback B1), `langstudent2@test.com` (id=47, A1).

| Metric | API source | DB source | Match |
|--------|-----------|-----------|-------|
| `current_streak` | `language_streaks.current_streak` | Same | Yes (0/0 in dev) |
| `longest_streak` | `language_streaks.longest_streak` | Same | Yes |
| `vocabulary_learned` | `language_vocabulary_progress` (known) | Same | Yes |
| `vocabulary_learning` | `language_vocabulary_progress` (learning) | Same | Yes |
| `vocabulary_count` | `language_analytics.vocabulary_count` | Same | Yes |
| `writing_completed` | `language_writing_progress.completed_at` | Same | Yes |
| `speaking_completed` | `language_speaking_progress.completed_at` | Same | Yes |
| Completion % | Rolled up in `skill_growth_json` | Derived from content + progress | Yes |

**Content availability (service smoke test):**

| Student | Reading | Vocab | Writing | Speaking |
|---------|---------|-------|---------|----------|
| id=5 (C1) | 5 @ B1 fallback | 20 @ B1 | 5 @ A1 | 5 @ A2 |
| id=47 (A1) | 5 @ A1 | 20 @ A1 | 5 @ A1 | 5 @ A2 |

Level fallback (highest published ≤ student level) works for listing. Analytics growth calculations for skills above B1 seed content may show `lessons_total: 0` until higher content is added — expected, not a data bug.

---

## 5. Parent Dashboard Integration

**Backend:** `GET /api/parent/dashboard` → `language_placement` via `_build_language_placement_summary()`.

**Fields exposed:**

- `language_code`, `reading_level`, `listening_level`, `writing_level`, `speaking_level`, `overall_level`
- `overall_calculation_method` (hardcoded `"bottleneck"`)
- `skill_growth`: reading, listening, writing, speaking, **vocabulary**

**Not exposed to parent (vs student `/progress`):**

- `current_streak`, `longest_streak`
- Completion percentages (reading/listening/writing/speaking)
- `vocabulary_learned` / `vocabulary_learning` as top-level counts (only inside `skill_growth.vocabulary`)
- `recent_activity`, `target_level`, `target_date`
- `primary_focus_skill`, `strength_skill`

**Frontend:** No parent Vue component references `language_placement` — **API-ready, UI not implemented**.

---

## 6. Database Tables (22 `language_*` tables)

| Table | Purpose | Used? |
|-------|---------|-------|
| `languages`, `language_products`, `language_subscriptions` | Catalog & billing | Yes |
| `language_student_profiles` | Onboarding / placement / targets | Yes |
| `language_placement_*` (4) | Placement flow | Yes |
| `language_assessments`, `language_assessment_skill_scores` | Scoring results | Yes |
| `language_learning_paths`, `language_path_items` | Generated path | Partial — hub counts only; items not auto-completed from lessons |
| `language_content_items` | All content (lessons, vocab, prompts) | Yes — 120 rows seeded |
| `language_reading_progress`, `language_listening_progress` | C1 lesson progress | Yes (empty until activity) |
| `language_writing_progress`, `language_speaking_progress` | C2 progress | Yes (empty until activity) |
| `language_vocabulary_progress` | C2 flashcard status | Yes (empty until activity) |
| `language_streaks`, `language_activity_log` | Engagement | Yes (empty in dev DB) |
| `language_analytics` | Rollup / parent summary | Yes |
| `language_certificates` | Phase B foundation | **Unused** — no issuance API or UI |

**Empty tables in dev DB** (no student practice yet): activity log, all progress tables, streaks, certificates. These are **not orphaned** — they are populated on first use.

**Unused column:** `language_analytics.weekly_minutes_json` — never written by any service.

---

## 7. Duplicate Logic

| Area | Locations | Risk |
|------|-----------|------|
| Reading ≈ Listening views | Two near-identical Vue files | Maintenance drift (listening lacks progress chips) |
| Writing ≈ Speaking list UI | Similar prompt list pattern | Low |
| `MediaRecorder` upload | Placement + Speaking views | Duplicated client code |
| Audio upload to disk | `language_placement_service` vs `language_media_service` | Backend duplication |
| Level ordering / fallback | `language_content_service`, `language_level_utils`, `language_learning_path_service` | `LEVEL_ORDER` repeated |
| Hub + progress builders | Both call `refresh_language_analytics` | Acceptable overlap |
| `fetchLanguageProduct` | Defined in `language.js` | **Dead code** — product comes via `/access` |

---

## 8. Bugs Found

### Critical (fixed during audit)

| # | Bug | Impact |
|---|-----|--------|
| B1 | Missing `WritingPromptOut` / `SpeakingPromptOut` imports in `language_student.py` | Router failed to load — all C2 endpoints unavailable |
| B2 | Placement `?results=1` set `showResults = false` | Hub “عرض النتائج” button broken |
| B3 | Reading/listening `access.redirect` returned without `router.push` | Unplaced users saw empty skill pages |
| B4 | Writing/Speaking `selectPrompt` uncaught errors; no `handleLanguageApiError` | Silent failures; no redirect to placement |

### Medium (open)

| # | Bug | Impact |
|---|-----|--------|
| B5 | Router guard swallows `fetchLanguageAccess` errors | Unsubscribed users may enter language routes on API failure |
| B6 | No router-level placement gate | Subscribed but unplaced students can deep-link to skill URLs (tabs hidden, pages load then redirect) |
| B7 | Analytics `_vocabulary_growth` uses raw CEFR level without content fallback | Students above B1 seed may show 0% vocab growth while cards list correctly |
| B8 | `language_path_items` not updated when lessons complete | Hub path progress may diverge from actual lesson completion |
| B9 | Listening audio assets may 404 | Graceful fallback UI exists; audio may be unavailable |
| B10 | Parent UI does not render `language_placement` | Parents cannot see language metrics in app |

### Low (open)

| # | Bug | Impact |
|---|-----|--------|
| B11 | `fetchLanguageProduct` unused in frontend | Dead code |
| B12 | `isLanguagePath()` unused in router | Dead code |
| B13 | Progress dashboard mixed EN/AR labels (“Current Streak”, “Vocabulary Learned”) | UX inconsistency |
| B14 | `language_certificates` table + model unused | Schema ready, no feature |
| B15 | `weekly_minutes_json` never populated | Dead analytics column |

---

## 9. Fixes Applied (this audit)

1. **`language_student.py`** — Added missing `WritingPromptOut`, `SpeakingPromptOut` imports.
2. **`StudentLanguagePlacementView.vue`** — `?results=1` now loads access + hub and displays completed placement results.
3. **`StudentLanguageReadingView.vue`** / **`StudentLanguageListeningView.vue`** — Redirect via `router.push(access.redirect)`; listening empty-list message added.
4. **`StudentLanguageWritingView.vue`** / **`StudentLanguageSpeakingView.vue`** — `handleLanguageApiError`, redirect on mount, try/catch on prompt load, empty/select states.
5. **Audit tooling** — Added `backend/scripts/audit_language_module.py` and `backend/scripts/audit_language_services.py` for repeatable checks.

No new features were added.

---

## 10. Remaining Limitations

1. **Content ceiling:** Seed content covers A1–B1 only. Students placed at C1/C2 see fallback content with info banner — by design until higher content ships.
2. **No AI evaluation:** Writing/speaking use rule-based scoring only (approved constraint).
3. **CEFR from placement only:** Practice updates `skill_growth_json`, not placement levels.
4. **Parent integration:** Backend payload complete for levels + skill growth; frontend parent dashboard not wired; streaks/completion not in parent API.
5. **Certificates:** Table exists; no PDF generation or award flow.
6. **Learning path:** Generated on placement submit; individual path items not marked complete via lesson APIs.
7. **No E2E test suite:** Manual / script-based verification only.
8. **Dev DB activity:** Progress/streak/activity tables empty — metrics verified at zero baseline, not after live practice.

---

## 11. Console Errors

No systematic frontend console errors were detected in code review. Potential runtime errors mitigated:

- Uncaught promise rejections in writing/speaking prompt load (fixed).
- Missing lazy-import target for vocabulary view (file exists — no import error).
- Microphone permission denial handled with user-facing alert in speaking/placement.

Recommend browser QA pass: placement flow, one lesson submit, one vocab review, one writing submit, one speaking record.

---

## 12. Readiness Assessment

| Area | Rating | Notes |
|------|--------|-------|
| Student routes & views | **Ready** | All 9 views present; stability fixes applied |
| Backend APIs | **Ready** | 25 routes; import bug fixed |
| Seeded content | **Ready** | 120 content items; migration chain intact |
| Progress accuracy | **Ready** | Metrics align with DB at zero baseline |
| Vocabulary C2 | **Ready** | 60 cards; UI label mapping correct |
| Writing / Speaking C2 | **Ready** | Rule scoring; upload flow implemented |
| Parent metrics API | **Partial** | Backend exposes core fields; UI missing; streaks/completion absent |
| Production hardening | **Needs work** | Router guards, E2E tests, parent UI, B7–B8 |

### Verdict

**Conditional Go for student-facing Language Module** in staging / pilot. Recommend addressing B5–B7 and parent UI before general production release.

---

## 13. Verification Commands

```bash
# DB revision + seed counts
cd backend && python scripts/verify_c2_seed.py

# Service-layer smoke test (student id)
cd backend && python scripts/audit_language_services.py 47

# Full audit (frontend files + TestClient + DB cross-check)
cd backend && python scripts/audit_language_module.py

# Table inventory
cd backend && python scripts/audit_language_tables.py
```

---

## 14. Migration Chain

```
0008_language_learning_phase1
  → 0009_language_phase2  (file: 0009_language_learning_phase2_placement.py)
  → 0010_language_c1
  → 0011_language_c2      ← current head
```

Verified on audit DB: `alembic_version = 0011_language_c2`.
