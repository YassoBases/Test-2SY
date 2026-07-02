# LANGUAGE-STT-MIGRATION-1.0

## Summary

Replaced the **Language module** speech-to-text pipeline with **OpenAI GPT-4o Transcribe** (`gpt-4o-transcribe`), with automatic fallback to the existing **faster-whisper** path when OpenAI is unavailable.

**No frontend changes. No database changes. No API contract changes.**

---

## Files modified

| File | Change |
|------|--------|
| `backend/app/services/language_transcription_service.py` | Primary STT implementation: OpenAI first, Whisper fallback |
| `backend/app/core/config.py` | Added `OPENAI_API_KEY`, `LANGUAGE_STT_PROVIDER`, `LANGUAGE_STT_MODEL` |
| `.env.example` | Documented new Language STT env vars |
| `backend/.env.example` | Documented new Language STT env vars |
| `docker-compose.yml` | Passed new env vars into API container |

---

## Old STT implementation

**File:** `backend/app/services/language_transcription_service.py`

**Flow:**
```
Language audio upload (.webm)
  → ffmpeg normalize → 16 kHz mono WAV
  → faster-whisper (LANGUAGE_CONVERSATION_WHISPER_MODEL, default small.en)
  → ConversationTranscription(engine="faster-whisper", ...)
```

**Consumers (unchanged imports):**
- `language_conversation_service.py` — conversation voice turns
- `language_speaking_feedback_service.py` — speaking prompt feedback
- `language_student.py` — scenario voice turns (`POST .../speaking/scenarios/.../voice`)

**Gate:** Required `ENABLE_WHISPER=true`.

---

## New GPT-4o Transcribe implementation

**File:** `backend/app/services/language_transcription_service.py`

**Flow (default):**
```
Language audio upload (.webm)
  → POST https://api.openai.com/v1/audio/transcriptions
      model = LANGUAGE_STT_MODEL (gpt-4o-transcribe)
      language = en
      prompt = LANGUAGE_CONVERSATION_WHISPER_INITIAL_PROMPT (or default)
  → ConversationTranscription(engine="openai", model="gpt-4o-transcribe", ...)
```

**Fallback (preserved):**
```
If OpenAI fails OR LANGUAGE_STT_PROVIDER=whisper OR OPENAI_API_KEY missing:
  → existing faster-whisper path (ffmpeg + small.en)
  → ConversationTranscription(engine="faster-whisper", meta.fallback=true)
```

**Gate:** OpenAI path runs when `LANGUAGE_STT_PROVIDER=openai` and `OPENAI_API_KEY` is set. Whisper fallback still requires `ENABLE_WHISPER=true`.

---

## Environment variables

```env
OPENAI_API_KEY=
LANGUAGE_STT_PROVIDER=openai
LANGUAGE_STT_MODEL=gpt-4o-transcribe
```

Set `LANGUAGE_STT_PROVIDER=whisper` to force the legacy faster-whisper path only.

Existing Whisper tuning vars remain for fallback:
- `LANGUAGE_CONVERSATION_WHISPER_MODEL`
- `LANGUAGE_CONVERSATION_WHISPER_COMPUTE_TYPE`
- `LANGUAGE_CONVERSATION_WHISPER_BEAM_SIZE`
- `LANGUAGE_CONVERSATION_WHISPER_VAD`
- `LANGUAGE_CONVERSATION_WHISPER_INITIAL_PROMPT`

---

## Confirmation: ONLY Language module uses GPT-4o Transcribe

| Area | STT engine | Evidence |
|------|------------|----------|
| **Language conversation** | `transcribe_english_audio()` → OpenAI / Whisper fallback | `language_conversation_service.py` |
| **Language speaking feedback** | same | `language_speaking_feedback_service.py` |
| **Language scenario voice** | same | `language_student.py` |
| Lesson / teacher voice samples | faster-whisper / Gemini | `voice_service.py` — **unchanged** |
| Lesson video transcription | faster-whisper → Gemini | `voice_service.py` — **unchanged** |
| Chat AI | none (text in) | **unchanged** |
| Planner | none | **unchanged** |
| OCR | Mistral | **unchanged** |
| Quiz generation | Gemini | **unchanged** |
| Parent / Teacher modules | no `transcribe_english_audio` usage | **unchanged** |

Repo search for `gpt-4o-transcribe` / `OPENAI_API_KEY` / `language_transcription_service` confirms OpenAI STT is confined to `language_transcription_service.py` and Language module callers.

---

## API contract preservation

`ConversationTranscription` dataclass fields unchanged:
- `text`, `engine`, `model`, `duration_s`, `avg_logprob`, `no_speech_prob`, `language_probability`, `low_confidence`, `raw_text`, `meta`

`transcribe_english_audio(data, suffix=...)` signature and return type unchanged.

Frontend and HTTP routes unchanged.

---

## Deployment note

Add to your `.env`:

```env
OPENAI_API_KEY=sk-...
LANGUAGE_STT_PROVIDER=openai
LANGUAGE_STT_MODEL=gpt-4o-transcribe
```

Without `OPENAI_API_KEY`, the Language module automatically falls back to faster-whisper (if `ENABLE_WHISPER=true`).
