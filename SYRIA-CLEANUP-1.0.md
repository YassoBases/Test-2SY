# SYRIA-CLEANUP-1.0 — Final Report

**Date:** 2026-07-03  
**Scope:** EduSpark Syria is the sole deployment. Germany branding, scripts, and shared-DB coupling removed. Arabic defaults enforced for core tutoring; English-learning module retained with Syrian audience context.

---

## 1. Backend startup (fixed)

| Issue | Fix |
|-------|-----|
| `ImportError: cannot import name '_review_schedule_gemini'` in `routine.py` | Imports/call updated to `_review_schedule_claude` |
| Unused imports `_generate_schedule_gemini`, `_log_gemini_usage` | Removed from `routine.py` |

**Verification:** `from app.main import app` succeeds. Uvicorn reaches `Application startup complete` against `eduspark_syria`. `http://127.0.0.1:8000/docs` returns **200**.

---

## 2. Germany references removed

### Frontend

| Location | Before | After |
|----------|--------|-------|
| `src/router/index.js` | `EduSpark Germany` | `EduSpark — منصة التعليم الذكي` / `EduSpark` |
| `index.html` | *(already Arabic)* | `EduSpark — منصة التعليم الذكي` |

### Backend AI locale (`backend/app/core/ai_locale.py`)

| Item | Before | After |
|------|--------|-------|
| Module docstring | Germany deployment, English | EduSpark Syria, Arabic |
| `AI_OUTPUT_LANGUAGE` | English | Arabic |
| `AI_LOCALE_TAG` | `en-DE` | `ar-SY` |
| Language rule | German secondary-school students | Syrian secondary-school students (`ENGLISH_MODULE_LANGUAGE_RULE`) |
| Tutor fallbacks / persona | English | Arabic |
| Quiz rules | English only | Arabic only |
| Keyword triggers | English | Arabic |
| Stopwords | English set | Arabic set |
| Transcribe prompts | English | Arabic (`STT_TRANSCRIBE_*`; legacy `GEMINI_TRANSCRIBE_*` aliases kept for STT fallbacks) |

### Service prompts (Germany → Syria)

| File | Change |
|------|--------|
| `language_coach_service.py` | German → Syrian secondary-school learners |
| `language_microlesson_service.py` | Same |
| `language_vocabulary_service.py` | Same |
| `language_conversation_prompts.py` | English tutor audience: Syrian students |
| `language_lesson_generation_service.py` | Germany/integration topics → Syrian/school-life; Claude docstrings |
| `routine_service.py` | Gemini → Claude/LLM logging |
| `lesson_curated_insights_service.py` | `_build_gemini_prompt` → `_build_curated_prompt` |

### Alembic comments

| File | Change |
|------|--------|
| `0042_adaptive_difficulty.py` | Removed Germany mixed-DB note |
| `0043_add_recent_scores_json.py` | Removed Germany/Syria mixed-DB note |

### Language seed JSON (`backend/alembic/seeds/language_content/`)

**16 files** rethemed (Germany cities/topics → Syria/neutral): e.g. Berlin/Frankfurt/Stuttgart → Damascus/Homs; `in Germany` → `in Syria`; Ausbildung/Pfand/Ruhezeit → neutral English terms.

**Manual fix:** `listening_A1.json` — distractor `Germany` → `Jordan`; `situation_ar` Berlin → Damascus.

---

## 3. Deleted files (Germany-only or obsolete)

| File | Reason |
|------|--------|
| `backend/scripts/verify_language_lesson_generation.py` | Germany parity script (`EduSpark-Germany` path) |
| `backend/scripts/verify_language_content_seed.py` | Compared seeds to Germany repo |
| `backend/scripts/parity_runtime_check.py` | Germany vs Syria runtime parity |
| `backend/scripts/repair_alembic_migration_chain.py` | Germany ghost revision repair |
| `backend/scripts/verify_migration_repair.py` | Mixed Germany/Syria simulation |
| `backend/scripts/_ocr_rootcause_probe.out.txt` | Probe artifact with Germany paths |
| `backend/scripts/voice_state_out.json` | Debug artifact with Germany upload paths |
| `backend/test_gemini.py` | Obsolete Gemini LLM test (LLM is Claude) |
| `backend/scripts/_syria_seed_retheme.py` | One-off seed tool (executed, removed) |

---

## 4. Renamed symbols (cosmetic Gemini cleanup, safe)

| Before | After | Notes |
|--------|-------|-------|
| `_build_gemini_prompt` | `_build_curated_prompt` | `lesson_curated_insights_service.py` |
| `_review_schedule_gemini` | `_review_schedule_claude` | `routine.py` → `routine_service.py` |
| `_log_gemini_usage` | `_log_llm_usage` | Alias `_log_gemini_usage` kept internally |

**Preserved aliases (STT / backward compat — not removed):**

- `generate_gemini_json` → `generate_llm_json` (`ai_service.py`)
- `GEMINI_LANGUAGE_RULE` → `ENGLISH_MODULE_LANGUAGE_RULE` (`ai_locale.py`)
- `GEMINI_TRANSCRIBE_*` → `STT_TRANSCRIBE_*` (`ai_locale.py`)
- `_transcribe_gemini_fallback`, `_transcribe_video_with_gemini` (Gemini STT fallbacks only)
- `GEMINI_API_KEY` in config (STT fallback gate only)

---

## 5. Configuration changes

| File | Change |
|------|--------|
| `.env` | `POSTGRES_DB=eduspark_syria` |
| `.env.example` | `POSTGRES_DB=eduspark_syria` |
| `backend/.env.example` | `POSTGRES_DB=eduspark_syria` |
| `.env.docker.example` | `DOCKER_POSTGRES_DB=eduspark_syria` |
| `docker-compose.yml` | Default DB `eduspark_syria` (db + backend services) |
| `backend/scripts/setup_local_db.sql` | Creates `eduspark_syria` instead of shared `eduspark` |

### New database tooling

| File | Purpose |
|------|---------|
| `backend/scripts/setup_syria_db.sql` | Create dedicated `eduspark_syria` role/DB |
| `backend/scripts/migrate_shared_db_to_syria.ps1` | `pg_dump` / `pg_restore` from legacy `eduspark` |

### Database migration performed (this machine)

1. Created PostgreSQL database **`eduspark_syria`**
2. Full copy from legacy **`eduspark`** via `pg_dump` + `pg_restore`
3. Syria data preserved; legacy `eduspark` left untouched as backup

**Action for other environments:** Run `setup_syria_db.sql`, then `migrate_shared_db_to_syria.ps1`, set `POSTGRES_DB=eduspark_syria`.

---

## 6. Arabic-by-default confirmation

| Area | Default |
|------|---------|
| `index.html` | `lang="ar"` `dir="rtl"` |
| `src/i18n/index.js` | `readStoredLocale()` → `'ar'` |
| `ai_locale.py` | Arabic tutor fallbacks, quiz rules, keywords |
| `ai_service.py` | Arabic answer budgets & tutor (unchanged) |
| `voice_service.py` | Syrian Arabic persona & Arabic video STT prompt |
| English Language module | Teaches **English** to Syrian students (by design) |

---

## 7. Preserved AI stack (unchanged)

| Capability | Status |
|------------|--------|
| Claude Sonnet 5 (primary LLM) | ✅ |
| Mistral OCR | ✅ |
| GPT-4o Transcribe (Language STT) | ✅ |
| Deepgram Nova (Student chat STT) | ✅ |
| ElevenLabs | ✅ |
| FAISS / BGE-M3 | ✅ |
| Gemini | STT fallback only (`GEMINI_API_KEY`) |

---

## 8. Files kept (uncertain / still required)

These were **not** deleted; they may reference legacy `gemini` names in verify scripts but remain useful for Syria QA:

- `backend/scripts/verify_lesson_video_transcription.py` — references `_transcribe_video_with_gemini` (STT)
- `backend/scripts/verify_lesson_chat_model_separation.py` — historical Gemini model checks
- `backend/scripts/verify_language_ai_scoring.py` — mocks `generate_gemini_json`
- `backend/scripts/phase2_verify.py` — `check_gemini_conversation` (may need Claude update later)
- All other `verify_language_*.py` scripts — Syria functional tests

**localStorage keys** (`eduspark_session`, `eduspark-locale`, `eduspark-ui-theme`) unchanged to avoid mass session loss; only DB name isolates Syria data.

**Legacy DB `eduspark`** on this host still exists as read-only backup after migration.

---

## 9. Confirmation: only EduSpark Syria remains

- ✅ No `Germany`, `EduSpark Germany`, or `EduSpark-Germany` references in active source (grep clean on tracked code/seeds)
- ✅ No Germany-only dev scripts in repo
- ✅ Dedicated database `eduspark_syria` configured and populated
- ✅ Backend imports and serves on port **8000**
- ✅ Branding, AI locale, and tutor defaults are **Syria / Arabic**

---

## 10. Recommended follow-ups (optional)

1. Re-seed or update **live** `language_content` rows in DB if Germany-themed content was already applied via Alembic (seed files are fixed for fresh installs).
2. Update `verify_lesson_chat_model_separation.py` / `phase2_verify.py` to assert Claude instead of Gemini LLM.
3. Remove legacy `eduspark` database on this machine once you confirm `eduspark_syria` is complete.
4. Set `ANTHROPIC_API_KEY` in `.env` if not already set for full LLM features.
