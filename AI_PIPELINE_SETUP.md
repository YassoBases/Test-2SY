# EduSpark AI Pipeline Setup

This project now has the notebook pipeline wired into FastAPI services.

## Backend Framework

The backend framework is FastAPI. The notebook Flask/ngrok cell is not used in the app.

## Pipeline Mapping

| Notebook step | FastAPI service |
| --- | --- |
| marker-pdf extraction | `backend/app/services/pdf_service.py` |
| BGE-M3 embeddings | `backend/app/services/embedding_service.py` |
| FAISS vector store | `backend/app/services/embedding_service.py` + `rag_service.py` |
| Whisper turbo transcription | `backend/app/services/voice_service.py` |
| Gemma via Ollama (optional dev fallback) | `backend/app/services/ai_service.py` |
| Gemini (primary LLM) | `backend/app/services/ai_service.py` + `GEMINI_API_KEY` |
| XTTS v2 voice output | `backend/app/services/tts_service.py` |

## Install Voice Upload Dependencies (required for teacher voice samples)

Teacher voice upload validation uses Whisper in `voice_validation_service.py`.
Install this **before** uploading a teacher voice sample:

```powershell
cd backend
.\venv\Scripts\python.exe -m pip install -r requirements-voice.txt
```

On Windows, keep `backend\venv` as a junction to a short path (see `run_local.ps1`) so PyTorch DLLs load correctly.

Restart uvicorn after installing. Use `backend\run_local.ps1` so the junction target Python is used.

## Install Full AI Dependencies (optional PDF pipeline)

From `backend/`:

```powershell
.\venv\Scripts\activate
.\venv\Scripts\python.exe -m pip install -r requirements-ai.txt
```

This installs marker, BGE-M3 support, FAISS, Whisper, PyTorch, and torchaudio.
`Pillow` is pinned to `10.4.0` because `marker-pdf` requires `Pillow<11`.

For scanned/image PDFs, install Tesseract OCR with Arabic language data or upload a text-based PDF. Without OCR, PyMuPDF can only read embedded/selectable text.

XTTS is optional and separated because `TTS` does not install cleanly on Python 3.12 Windows:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-tts.txt
```

Use Python 3.10/3.11, WSL, or a Docker AI worker for XTTS if this command fails.

## Gemini API (primary LLM)

Set your API key in `.env`:

```env
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.5-flash
LLM_PROVIDER=gemini
```

Gemini powers student chat, quiz generation, persona prompts, planner interpretation, routine/planner flows, and PDF OCR when configured.

## Ollama (optional local dev fallback)

To use a local model instead of Gemini, install Ollama from https://ollama.com, then:

```powershell
ollama pull gemma3
ollama serve
```

Set in `.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gemma3
```

Check it:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

## Environment Flags

These are in `.env`:

```env
# Fast local default. Switch to marker/FAISS only after model caches are ready.
PDF_EXTRACTOR=pymupdf
ENABLE_FAISS=false
EMBEDDING_MODEL=BAAI/bge-m3
ENABLE_WHISPER=true
WHISPER_MODEL=turbo
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.5-flash
LLM_PROVIDER=gemini
ENABLE_TTS=false
TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
```

If you want the notebook-heavy path after models are available locally:

```env
PDF_EXTRACTOR=marker
ENABLE_FAISS=true
```

Turn on XTTS only after installing `TTS`:

```env
ENABLE_TTS=true
```

## Student Voice Chat

The frontend now records a student voice question from the chat input. The backend endpoint is:

```text
POST /api/student/chat/voice
```

It transcribes audio with Whisper, retrieves lesson context through FAISS/keyword RAG, generates the reply with Gemini (or Ollama when `LLM_PROVIDER=ollama`), and optionally returns an XTTS audio URL.
