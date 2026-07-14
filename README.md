# EduSpark Syria — منصة التعليم الذكي

EduSpark Syria is an AI-powered, Arabic-first (RTL) learning platform for Syrian
secondary-school students, their teachers, and their parents. It combines an
adaptive AI tutor, lesson/notebook generation from uploaded PDFs, a standalone
English **Language module** (placement, lessons, speaking, listening, writing),
voice interaction, gamification, messaging, and parent monitoring.

- **Frontend:** Vue 3 + Vuetify 3 (RTL, Arabic by default) built with Vite.
- **Backend:** FastAPI + SQLAlchemy (async) on PostgreSQL, migrated with Alembic.
- **AI:** Claude Sonnet 5 for text/JSON, plus best-in-class providers for OCR,
  speech-to-text, text-to-speech, and retrieval (RAG). Every provider degrades
  gracefully — the app runs even with **no** API keys configured.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [AI Providers](#ai-providers)
5. [Models](#models)
6. [Database](#database)
7. [Troubleshooting](#troubleshooting)
8. [Project Structure](#project-structure)
9. [License](#license)
10. [Contributors](#contributors)

---

## Architecture

```
┌──────────────┐        HTTP / Bearer JWT        ┌──────────────────────┐
│  Vue 3 SPA   │  ───────────────────────────▶   │   FastAPI backend     │
│  (Vuetify,   │  ◀───────────────────────────   │   (async SQLAlchemy)   │
│   RTL i18n)  │        JSON / streamed           └───────────┬───────────┘
└──────────────┘                                              │
                                                              ▼
                                                    ┌──────────────────┐
                                                    │   PostgreSQL 14+  │
                                                    │  (Alembic schema) │
                                                    └──────────────────┘
                                                              │
                     ┌────────────────────────────────────────┴───────────────────────────┐
                     ▼                        ▼                        ▼                     ▼
              Text / JSON              Documents (OCR)          Speech-to-Text          Text-to-Speech
          ┌───────────────┐        ┌───────────────┐      ┌────────────────────┐   ┌───────────────┐
          │ Claude Sonnet │        │  Mistral OCR  │      │ Deepgram Nova (chat)│   │  ElevenLabs   │
          │      5        │        └───────────────┘      │ GPT-4o Transcribe   │   │  (voice TTS)  │
          │ (Anthropic)   │                               │   (Language module) │   └───────────────┘
          └───────────────┘                               │ Whisper / Gemini    │
                     │                                     │   (fallbacks)       │
                     ▼                                     └────────────────────┘
          ┌───────────────────────────┐
          │  RAG: BGE-M3 embeddings +  │
          │  FAISS vector search       │
          └───────────────────────────┘
```

**AI stack at a glance:**

| Capability | Primary | Fallback(s) |
|---|---|---|
| Text & JSON generation (tutor, lessons, quizzes, insights) | **Claude Sonnet 5** (Anthropic) | Ollama (optional local LLM) |
| Document OCR (PDF/image → text) | **Mistral OCR** | PyMuPDF text extraction |
| Language module speech-to-text (English) | **GPT-4o Transcribe** (OpenAI) | Faster-Whisper → Gemini |
| Student lesson voice chat speech-to-text (Arabic) | **Deepgram Nova** | Gemini |
| Teacher voice cloning / lesson audio & Language TTS | **ElevenLabs** / Supertonic | gTTS |
| Lesson RAG (semantic retrieval over lesson content) | **FAISS** + **BGE-M3** embeddings | keyword fallback |
| Lesson video transcription | **Faster-Whisper** (large-v3-turbo) | Gemini |

---

## Requirements

| Tool | Version | Notes |
|---|---|---|
| **Python** | 3.10 – 3.12 | Backend (FastAPI, SQLAlchemy 2, Alembic) |
| **Node.js** | 20.19+ or 22.12+ | Required by Vite 8 |
| **PostgreSQL** | 14+ | pgvector **optional** (off by default) |
| **FFmpeg** | any recent | Required for voice/Whisper features (audio decoding) |
| **Git** | any recent | Clone & version control |
| **Docker** | optional | Full-stack containers (see [DOCKER.md](./DOCKER.md)) |

> **pgvector is optional.** The default `ENABLE_PGVECTOR=false` and the schema
> does not require it. You do not need to install the extension to run the app.

> **FFmpeg** is only needed if you enable voice/Whisper features. Install via
> `winget install Gyan.FFmpeg` (Windows), `brew install ffmpeg` (macOS), or
> `sudo apt install ffmpeg` (Linux), and ensure it is on your `PATH`.

---

## Installation

### 1. Clone

```bash
git clone https://github.com/hamzakuzbari1/Test_SY.git
cd Test_SY
```

### 2. Environment variables

```bash
# from the project root
cp .env.example .env
```

Then edit `.env`. The only values required to start are the database settings;
AI keys are optional (see [AI Providers](#ai-providers)).

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password_here
POSTGRES_DB=eduspark_syria
DEBUG=true
VITE_API_URL=http://127.0.0.1:8000
```

> **Security note:** In production set `DEBUG=false` and provide a strong random
> `JWT_SECRET` (the app refuses to start with a placeholder secret when
> `DEBUG=false`). Generate one with:
> `python -c "import secrets; print(secrets.token_urlsafe(64))"`.

### 3. Database (create it once)

**Fresh install** — create the database and (optionally) a dedicated user:

```bash
psql -U postgres -f backend/scripts/setup_local_db.sql
```

Or manually (e.g. in pgAdmin):

```sql
CREATE DATABASE eduspark_syria;
CREATE USER eduspark WITH PASSWORD 'eduspark' LOGIN;
GRANT ALL PRIVILEGES ON DATABASE eduspark_syria TO eduspark;
```

> Prefer restoring an existing team backup instead? See
> [Database → Restore a backup](#database) — no Alembic migration is needed
> after restoring the latest backup.

### 4. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt

# Create the full schema + reference seed (required on a fresh database)
alembic upgrade head

# Seed test accounts (student / teacher / parent)
python scripts/seed_test_users.py

# (optional) sanity-check connection & configuration
python scripts/verify_setup.py

# Run the API
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API: <http://127.0.0.1:8000>
- Swagger docs: <http://127.0.0.1:8000/docs>

Optional extra dependencies (install only what you need):

```bash
pip install -r requirements-voice.txt          # voice upload / Whisper / TTS
pip install -r requirements-ai.txt             # extended AI helpers
pip install -r requirements-language-ai.txt    # Language module speaking/STT stack
```

#### GPU Acceleration (Optional)

Language module **Supertonic TTS** can use an NVIDIA GPU for faster speech synthesis.
**This is completely optional** — fresh clones and CPU-only machines work normally
with no NVIDIA hardware and no extra packages.

Only install if you have an NVIDIA GPU and want faster listening/conversation audio:

```bash
pip uninstall -y onnxruntime
pip install -r requirements-supertonic-gpu.txt
```

Requirements: NVIDIA GPU, recent driver, and the backend venv with
`requirements.txt` + `requirements-voice.txt` already installed.

At startup the backend logs `Supertonic ONNX Provider: CUDAExecutionProvider` or
`Supertonic ONNX Provider: CPUExecutionProvider`. Teammates without the GPU package
always get CPU — no `.env` changes required.

### 5. Frontend

```bash
# from the project root
npm install
npm run dev      # dev server → http://localhost:5173
npm run build    # production bundle
npm run preview  # preview the production build
```

### 6. Test accounts (after `seed_test_users.py`)

| Role | Email | Password |
|---|---|---|
| Student | test.auth.student@eduspark-test.dev | TestOnly123! |
| Teacher | test.auth.teacher@eduspark-test.dev | TestOnly123! |
| Parent | test.auth.parent@eduspark-test.dev | TestOnly123! |

You can also register a new account directly from the sign-up UI.

### 7. Running AI providers

AI features activate automatically once the relevant key is present in `.env`.
No key is required to boot the app — features without a key simply return a
friendly "not configured" message or use a fallback. See the next section.

---

## AI Providers

Add keys to `.env` to enable each capability. **All keys are optional** for the
server to start; each provider fails gracefully.

| Provider | Env var | Required for | Optional? | Fallback |
|---|---|---|---|---|
| **Anthropic (Claude Sonnet 5)** | `ANTHROPIC_API_KEY` | AI tutor, lesson/quiz/insight generation, all text & JSON | Optional (core AI features disabled without it) | Ollama local LLM if `LLM_PROVIDER=ollama` |
| **Mistral OCR** | `MISTRAL_API_KEY` | Extracting text from uploaded PDFs/images | Optional | PyMuPDF built-in text extraction |
| **OpenAI (GPT-4o Transcribe)** | `OPENAI_API_KEY` | Language module (English) speech-to-text | Optional | Faster-Whisper → Gemini |
| **Deepgram (Nova)** | `DEEPGRAM_API_KEY` | Student lesson voice chat STT (Arabic) | Optional | Gemini |
| **ElevenLabs** | `ELEVENLABS_API_KEY` | Teacher voice cloning, lesson TTS | Optional | gTTS |
| **Google Gemini** | `GEMINI_API_KEY` | STT **fallback only** (not used as an LLM) | Optional | — |
| **Resend** | `RESEND_API_KEY` | Transactional email (verification, 2FA OTP) | Optional | console/no-op in dev |
| **Ollama** | `OLLAMA_BASE_URL` / `OLLAMA_MODEL` | Optional local LLM fallback for Claude | Optional | — |

**Provider selection knobs (in `.env`):**

- `LLM_PROVIDER=claude` (default) or `ollama`
- `LANGUAGE_STT_PROVIDER=openai` (default) — English STT for the Language module
- `TTS_PROVIDER=elevenlabs` and `LANGUAGE_TTS_PROVIDER=supertonic`
- `ENABLE_FAISS`, `ENABLE_EMBEDDINGS`, `ENABLE_WHISPER`, `ENABLE_TTS`,
  `ENABLE_PGVECTOR` toggle heavier subsystems.

---

## Models

| Model | Role | Where it is used | Optional download |
|---|---|---|---|
| **Claude Sonnet 5** (`CLAUDE_MODEL=claude-sonnet-5`) | Primary LLM — all text & JSON generation | AI tutor, lesson/notebook generation, quiz generation, curated insights, routine/exam JSON | No (API) |
| **Mistral OCR** (`mistral-ocr-latest`) | Optical character recognition | PDF/image ingestion for lessons | No (API) |
| **GPT-4o Transcribe** (`gpt-4o-transcribe`) | English speech-to-text | Language module speaking/listening | No (API) |
| **Deepgram Nova** (`nova-3`) | Arabic speech-to-text | Student lesson voice chat | No (API) |
| **ElevenLabs** (`eleven_multilingual_v2`) | Text-to-speech / voice cloning | Teacher AI voice, lesson audio | No (API) |
| **BGE-M3** (`BAAI/bge-m3`) | Multilingual embeddings for RAG | Lesson content retrieval | **Yes** — downloaded from Hugging Face on first use |
| **FAISS** (CPU) | Vector similarity index | RAG search over embedded lesson chunks | No (pip package) |
| **Faster-Whisper** (`large-v3-turbo`, `small.en`) | Local speech-to-text | Lesson video transcription; Language STT fallback | **Yes** — model weights download on first use |
| **Gemini** (`gemini-2.5-flash`) | STT fallback | Fallback for Deepgram / Whisper failures | No (API) |
| **Supertonic** (`M1` voice) | Language module TTS | English speaking practice playback | **Yes** — `LANGUAGE_SUPERTONIC_AUTO_DOWNLOAD=true` fetches assets |
| **Ollama** (`gemma3`) | Optional local LLM | Offline fallback for Claude | **Yes** — pulled via Ollama |

> Model downloads (BGE-M3, Whisper, Supertonic) are cached under the paths set by
> `HF_HOME` / `HUGGINGFACE_HUB_CACHE` / `SENTENCE_TRANSFORMERS_HOME`, or your
> default cache directory. Set `ENABLE_FAISS=false` / `ENABLE_WHISPER=false` for
> a lightweight run with no local model downloads.

---

## Database

### Fresh install

1. Create the database (`setup_local_db.sql` or the manual SQL above).
2. From `backend/`, run `alembic upgrade head` to build the full schema and seed
   canonical reference data (roles, languages, placement content, etc.).
3. Run `python scripts/seed_test_users.py` to create test accounts.

The migration history has been squashed into a clean baseline
(`0001_baseline` → `0002_reference_seed`), so `alembic upgrade head` works on an
empty database in one pass.

### Restore a backup

If your team shares a PostgreSQL backup:

```bash
# create an empty database first
createdb -U postgres eduspark_syria

# restore (choose the form matching your dump)
pg_restore -U postgres -d eduspark_syria path/to/backup.dump
# or, for a plain SQL dump:
psql -U postgres -d eduspark_syria -f path/to/backup.sql
```

> **No migration required after restoring the latest team backup.** The current
> codebase matches the latest backup schema, so you can restore and immediately
> run the backend — do **not** run `alembic upgrade head` on a restored backup.

---

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| `Connection refused` on port 5432 | PostgreSQL isn't running — start the service. |
| `password authentication failed` | Fix `POSTGRES_USER` / `POSTGRES_PASSWORD` in `.env`. See [LOCAL_SETUP.md](./LOCAL_SETUP.md). |
| `relation "users" does not exist` | Run `alembic upgrade head` from the `backend/` folder (fresh DB only). |
| Can't log in | Run `python scripts/seed_test_users.py`. |
| Server won't start with `JWT_SECRET ... insecure` | Set a strong `JWT_SECRET`, or keep `DEBUG=true` for local dev. |
| `uvicorn: command not found` | Use `python -m uvicorn app.main:app ...` inside the backend venv. |
| Missing API key / "not configured" responses | Add the relevant key to `.env` (see [AI Providers](#ai-providers)). The app still runs without keys. |
| `ffmpeg not found` / audio errors | Install FFmpeg and ensure it is on your `PATH`. |
| Torch / FAISS install issues | Reinstall with the CPU index: `pip install -r requirements.txt` (uses `--extra-index-url https://download.pytorch.org/whl/cpu`). |
| First Whisper/embedding call is slow | Model weights download & cache on first use — subsequent calls are fast. Set `ENABLE_WHISPER=false` / `ENABLE_FAISS=false` to skip. |
| Node version error on `npm run dev` | Upgrade Node to 20.19+ or 22.12+. |
| Frontend can't reach the API | Ensure `VITE_API_URL=http://127.0.0.1:8000` and the backend is running. |
| Port already in use | Change the uvicorn `--port`, the Vite port, or (Docker) `POSTGRES_PUBLISH_PORT`. |

---

## Project Structure

```
EduSpark-Syrian/
├── backend/                     FastAPI backend
│   ├── app/
│   │   ├── api/                 HTTP routers (auth, student, teacher, parent, language, ...)
│   │   ├── services/            AI + business logic (claude_service, mistral_ocr_service,
│   │   │                        language_*_service, voice_service, student_chat_stt_service, ...)
│   │   ├── models/              SQLAlchemy ORM models
│   │   ├── schemas/             Pydantic request/response schemas
│   │   ├── core/                config, security, AI locale (Arabic-first)
│   │   └── main.py              FastAPI app entry point
│   ├── alembic/                 Migrations (0001_baseline, 0002_reference_seed) + seeds/ + sql/
│   ├── scripts/                 setup_local_db.sql, seed_test_users.py, verify_setup.py, ...
│   ├── requirements*.txt        core + ai + language-ai + voice + optional supertonic-gpu
│   └── uploads/                 local PDF/audio uploads (git-ignored, auto-created)
├── src/                         Vue 3 + Vuetify frontend
│   ├── views/                   pages (student, teacher, parent, onboarding, languages, ...)
│   ├── components/              reusable UI components
│   ├── api/                     axios API clients
│   ├── composables/             shared reactive logic
│   ├── locales/                 i18n bundles (ar default, en, fr)
│   └── router/                  vue-router routes
├── public/language-assets/      shipped Language-module audio (placement listening, etc.)
├── docs/                        architecture & feature docs (ERD, SYSTEM_ARCHITECTURE, ...)
├── deploy/ , docker-compose.yml Docker deployment (optional)
├── .env.example                 environment template (copy to .env)
└── README.md
```

---

## License

Proprietary — © 2026 MozaicAI Solutions. All rights reserved.
This repository is for the EduSpark Syria team and is not licensed for public
redistribution. Replace this section with an OSI license (e.g. MIT) if the
project is later open-sourced.

---

## Contributors

Built and maintained by the **EduSpark Syria team** at **MozaicAI Solutions**.

Contributions from team members are welcome via pull requests. Please keep
secrets out of commits (`.env` is git-ignored) and follow the existing project
structure and conventions.
