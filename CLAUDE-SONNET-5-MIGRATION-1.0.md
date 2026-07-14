# CLAUDE-SONNET-5-MIGRATION-1.0

Migration of **all runtime Gemini LLM integrations** to **Claude Sonnet 5** via a centralized `claude_service` layer.

**Not migrated (by design):** OCR (Mistral), Language STT (OpenAI), Student Chat STT (Deepgram), TTS (ElevenLabs), Faster-Whisper local STT.

---

## Architecture

```
Feature code
  → ai_service.generate_llm_json() / generate_tutor_reply() / generate_planner_interpretation()
  → claude_service (Anthropic SDK)
  → CLAUDE_MODEL (default: claude-sonnet-5)
```

**Config (add to `.env`):**
```env
ANTHROPIC_API_KEY=
CLAUDE_MODEL=claude-sonnet-5
LLM_PROVIDER=claude
```

`GEMINI_API_KEY` is **retained only** for STT fallback paths (not LLM).

---

## New files

| File | Purpose |
|------|---------|
| `backend/app/services/claude_service.py` | Central Anthropic integration: text, JSON, audio-assessment (via Language STT transcript) |

---

## Modified files

| File | Change |
|------|--------|
| `backend/app/core/config.py` | `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`, `LLM_PROVIDER=claude`; removed `GENAI_EXAM_MODEL`, `LESSON_CHAT_MODEL` |
| `backend/app/services/ai_service.py` | Tutor chat, planner, `generate_llm_json()` (alias `generate_gemini_json`) |
| `backend/app/services/chat_visual_service.py` | Claude JSON for visual decisions |
| `backend/app/services/quiz_service.py` | `_call_claude_text()` |
| `backend/app/services/routine_service.py` | `_extract_with_claude`, `_generate_schedule_claude`, `_review_schedule_claude` |
| `backend/app/services/routine_exam_json_service.py` | Post-OCR JSON structuring via Claude |
| `backend/app/services/lesson_curated_insights_service.py` | `_generate_claude_insights()` |
| `backend/app/services/voice_service.py` | `build_persona_prompt()` LLM → Claude (STT fallbacks unchanged) |
| `backend/app/services/language_exam_genai.py` | Speaking exam → Claude + Language STT transcript |
| `backend/app/services/language_exam_service.py` | All exam text LLM → `generate_llm_json` |
| `backend/app/services/language_placement_ai_scoring.py` | Writing/speaking scoring → Claude |
| `backend/app/services/language_pronunciation_service.py` | Pronunciation → Claude + Language STT |
| `backend/app/services/language_speaking_feedback_service.py` | Tutor reply → Claude |
| `backend/app/services/language_conversation_ai_service.py` | Conversation JSON → Claude |
| `backend/app/services/language_*` (12 services) | `generate_llm_json` + `is_claude_configured()` |
| `backend/app/services/speaking_coach_service.py` | Claude JSON |
| `backend/app/api/routine.py` | `ANTHROPIC_API_KEY` gate for exam OCR structuring |
| `backend/requirements.txt` | Added `anthropic>=0.49.0` |
| `.env.example`, `backend/.env.example`, `docker-compose.yml` | Claude env vars |
| `.env` | Claude section added; Gemini kept for STT only |

---

## Gemini → Claude call mapping

| Feature | Previous model | New model | Entry point |
|---------|----------------|-----------|-------------|
| Student Lesson Chat | `gemini-3.1-flash-lite` | `claude-sonnet-5` | `generate_tutor_reply()` |
| Chat Visuals | `gemini-3.1-flash-lite` | `claude-sonnet-5` | `decide_chat_visual()` |
| Quiz generation | `gemini-2.5-flash` | `claude-sonnet-5` | `quiz_service._call_claude_text()` |
| Planner interpretation | `gemini-2.5-flash` | `claude-sonnet-5` | `generate_planner_interpretation()` |
| Routine extraction/schedule/review | `gemini-2.5-flash` | `claude-sonnet-5` | `routine_service` |
| Routine exam JSON (post-OCR) | `gemini-2.5-flash` | `claude-sonnet-5` | `routine_exam_json_service` |
| Lesson curated insights | `gemini-3.1-flash-lite` | `claude-sonnet-5` | `_generate_claude_insights()` |
| Teacher persona | `gemini-2.5-flash` | `claude-sonnet-5` | `build_persona_prompt()` |
| Language module (all JSON LLM) | `gemini-2.5-flash` | `claude-sonnet-5` | `generate_llm_json()` |
| Language exam (text) | `gemini-2.5-flash` | `claude-sonnet-5` | `language_exam_service` |
| Language exam (speaking audio) | `gemini-2.5-flash` (native audio) | `claude-sonnet-5` + GPT-4o transcript | `language_exam_genai` |
| Placement speaking | `gemini-2.5-flash` (native audio) | `claude-sonnet-5` + GPT-4o transcript | `language_placement_ai_scoring` |
| Pronunciation AI | `gemini-2.5-flash` (native audio) | `claude-sonnet-5` + GPT-4o transcript | `language_pronunciation_service` |

---

## Remaining Gemini references (intentional)

| File | Purpose | Type |
|------|---------|------|
| `voice_service.py` | Lesson video STT fallback | **STT** (unchanged) |
| `voice_service.py` | Teacher/lesson audio STT fallback | **STT** (unchanged) |
| `student_chat_stt_service.py` | Student chat STT fallback after Deepgram | **STT** (unchanged) |
| `backend/app/core/config.py` | `GEMINI_API_KEY`, `GEMINI_MODEL` for STT fallbacks | Config |
| `backend/requirements.txt` | `google-generativeai` still listed | Package (not removed until verified) |
| `backend/test_gemini.py` | Dead dev script | Not runtime |
| `ai_service.py` | `generate_gemini_json = generate_llm_json` | Backward-compat alias |

**No runtime Gemini LLM calls remain.**

---

## Gemini fallbacks still present

| Path | Still uses Gemini? | Notes |
|------|---------------------|-------|
| Deepgram fails → student chat STT | **Yes** | STT only — not LLM |
| Whisper fails → teacher/lesson audio STT | **Yes** | STT only |
| Whisper fails → lesson video STT | **Yes** | STT only |
| Ollama fails → any LLM | **No** → Claude | `LLM_PROVIDER=ollama` tries Ollama first, then Claude |
| OpenAI STT fails → Language module | **No** → Whisper | Unchanged |

---

## Audio LLM scoring note

Claude does not support native audio input. Audio-native features (exam speaking, placement speaking, pronunciation) now:

1. Transcribe with **existing Language STT** (OpenAI GPT-4o Transcribe — unchanged provider)
2. Evaluate with **same rubric prompts** via Claude

Prompts, JSON schemas, and parsing are preserved; delivery assessment is inferred from transcript disfluencies instead of raw waveform.

---

## Packages

| Package | Status |
|---------|--------|
| `anthropic` | **Added** — required |
| `google-generativeai` | **Still in requirements** — needed for STT fallbacks; remove after STT fallbacks are migrated |
| `google-genai` | **Not in requirements.txt** — was only used by old `language_exam_genai.py` (now Claude) |

**Install before restart:**
```bash
pip install anthropic>=0.49.0
```

---

## Final status table

| Feature | Previous | New | Status |
|---------|----------|-----|--------|
| Student Chat | Gemini | Claude Sonnet 5 | ✅ |
| Chat Visuals | Gemini | Claude Sonnet 5 | ✅ |
| Quiz | Gemini | Claude Sonnet 5 | ✅ |
| Planner | Gemini | Claude Sonnet 5 | ✅ |
| Routine | Gemini | Claude Sonnet 5 | ✅ |
| Lesson Insights | Gemini | Claude Sonnet 5 | ✅ |
| Teacher Persona | Gemini | Claude Sonnet 5 | ✅ |
| Language Conversation | Gemini | Claude Sonnet 5 | ✅ |
| Language Exam | Gemini | Claude Sonnet 5 | ✅ |
| Placement / Pronunciation | Gemini (audio) | Claude + GPT-4o transcript | ✅ |
| OCR | Mistral | Unchanged | ✅ |
| Language STT | GPT-4o Transcribe | Unchanged | ✅ |
| Student STT | Deepgram Nova | Unchanged | ✅ |
| ElevenLabs | Unchanged | Unchanged | ✅ |
| Gemini STT fallbacks | Gemini | Unchanged (STT only) | ⚠️ intentional |

---

## Activation

1. Set `ANTHROPIC_API_KEY=...` in `.env`
2. `pip install anthropic>=0.49.0`
3. Restart backend

No API key required for code to load; LLM features return empty/unavailable until the key is set.
