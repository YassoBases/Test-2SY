# Language Hardening Sprint — Report

**Date:** 2026-06-02  
**Scope:** Production-readiness fixes from `LANGUAGE_MODULE_AUDIT.md` — no certificates, no AI, no new features.

---

## 1. Issues Fixed

### Router guard hardening (`src/router/index.js`)

| Before | After |
|--------|-------|
| Only checked subscription; swallowed API errors | Full access rules on every `languageModule` route |
| Unplaced students could open skill URLs directly | Skill routes redirect to placement |
| Subscribed users could revisit paywall inconsistently | Subscribe route redirects forward when already subscribed |

**Guard rules:**

| Route | Not subscribed | Subscribed, no placement | Subscribed + placement |
|-------|----------------|--------------------------|------------------------|
| `/languages/subscribe` | Allow | → placement or hub | → hub |
| `/languages` (hub) | → subscribe | Allow | Allow |
| `/languages/placement` | → subscribe | Allow | Allow |
| Reading/listening/vocab/writing/speaking/progress | → subscribe | → placement | Allow |

API failure on access check redirects to hub (except when already navigating to hub).

### Parent API metrics (`parent_monitoring_service.py`, `schemas/parent.py`)

Extended `LanguagePlacementSummaryOut` and `_build_language_placement_summary()` with:

- `vocabulary_count`, `vocabulary_learned`
- `current_streak`, `longest_streak`
- `completed_activities`, `writing_completed`, `speaking_completed`

Parent summary now calls `refresh_language_analytics()` so metrics match student progress dashboard.

### Parent UI (`ParentLanguageSection.vue`, `ParentDashboardView.vue`, `useParentMonitor.js`)

New read-only section on parent dashboard showing:

- Reading / listening / writing / speaking / overall levels
- Skill growth % per skill
- Vocabulary count & learned count
- Streaks, completed activities, writing/speaking completion counts

Hidden when child has no `language_placement` data (no language analytics row).

### Analytics consistency (`language_analytics_service.py`)

| Fix | Detail |
|-----|--------|
| Content level fallback | `_skill_growth_for_level` uses `resolve_content_level()` — C1+ students count B1 (or highest available) content |
| Vocabulary growth | `_vocabulary_growth` uses same fallback; known/learning counts scoped to active content deck lemmas only |
| `content_level` field | Added to skill growth payloads for transparency (student level vs content level) |
| Public alias | `resolve_content_level` exported from `language_content_service.py` |

**Verified:** `backend/scripts/verify_analytics_fallback.py` — student id=5 (reading C1) gets reading `lessons_total=5`, vocabulary `total_words=20` at B1 fallback.

---

## 2. Routes Verified

All 9 language routes covered by hardened guard:

| Route | Guard behavior |
|-------|----------------|
| `student-languages` | Hub — requires subscription |
| `student-languages-subscribe` | Paywall — forward if subscribed |
| `student-languages-placement` | Requires subscription |
| `student-languages-reading` | Requires subscription + placement |
| `student-languages-listening` | Requires subscription + placement |
| `student-languages-vocabulary` | Requires subscription + placement |
| `student-languages-writing` | Requires subscription + placement |
| `student-languages-speaking` | Requires subscription + placement |
| `student-languages-progress` | Requires subscription + placement |

---

## 3. Parent Dashboard Coverage

| Metric | Backend | Parent UI |
|--------|---------|-----------|
| Reading level | Yes | Yes |
| Listening level | Yes | Yes |
| Writing level | Yes | Yes |
| Speaking level | Yes | Yes |
| Overall level | Yes | Yes |
| Skill growth (per skill) | Yes | Yes (% shown) |
| Vocabulary count | Yes | Yes |
| Vocabulary learned | Yes | Yes |
| Current streak | Yes | Yes |
| Longest streak | Yes | Yes |
| Completed activities | Yes | Yes |
| Writing completed | Yes | Yes |
| Speaking completed | Yes | Yes |

**Not shown on parent UI (by design — student-only detail):**

- Recent activity feed (general activity timeline still on dashboard)
- Reading/listening completion % bars
- Target level / target date
- Primary focus / strength labels

---

## 4. Files Changed

| File | Change |
|------|--------|
| `src/router/index.js` | Language guard hardening |
| `backend/app/services/language_analytics_service.py` | Content fallback in growth calculations |
| `backend/app/services/language_content_service.py` | Export `resolve_content_level` |
| `backend/app/services/parent_monitoring_service.py` | Extended language summary |
| `backend/app/schemas/parent.py` | Extended `LanguagePlacementSummaryOut` |
| `src/components/parent/ParentLanguageSection.vue` | **New** — language panel |
| `src/views/parent/ParentDashboardView.vue` | Integrate language section |
| `src/composables/useParentMonitor.js` | Expose `languagePlacement` |
| `backend/scripts/verify_analytics_fallback.py` | **New** — regression check |

---

## 5. Remaining Limitations

1. **Content ceiling** — Seed content A1–B1; C1+ students use fallback content (now consistent in analytics too).
2. **No certificates** — Out of scope for this sprint.
3. **No AI evaluation** — Out of scope.
4. **Learning path items** — Hub path counts still not synced with lesson completion APIs.
5. **Parent UI** — No completion % bars or recent language activity (only aggregate metrics).
6. **`weekly_minutes_json`** — Still unused column in analytics.
7. **`language_certificates` table** — Still unused (Phase B foundation).
8. **E2E tests** — Guard and parent UI not yet covered by automated browser tests.
9. **Dead code** — `fetchLanguageProduct`, `isLanguagePath()` still unused (low priority).

---

## 6. Verification Commands

```bash
# Analytics fallback (C1 student → B1 content counts)
cd backend && python scripts/verify_analytics_fallback.py

# Service smoke test
cd backend && python scripts/audit_language_services.py 5

# Full module audit (from prior sprint)
cd backend && python scripts/audit_language_module.py
```

---

## 7. Readiness Assessment

| Area | Status |
|------|--------|
| Router access control | **Ready** |
| Parent metrics API | **Ready** |
| Parent dashboard UI | **Ready** |
| Analytics / C1+ consistency | **Ready** |
| Student flows (Phases A–C2) | **Ready** (unchanged behavior, hardened gates) |

**Verdict:** Language Module meets hardened production-readiness criteria for student + parent monitoring paths. Certificates and AI remain explicitly deferred.
