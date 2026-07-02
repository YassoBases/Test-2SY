# EduSpark Backend

## Docker

From project root: `docker compose up --build` — see [../DOCKER.md](../DOCKER.md).

FastAPI + PostgreSQL (local) + pgvector + optional Gemini.

## Local run (no Docker)

```bash
# 1. PostgreSQL running on localhost with pgvector
psql -U postgres -f scripts/setup_local_db.sql

# 2. From backend/
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-voice.txt

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Docs: http://127.0.0.1:8000/docs

Loads `.env` from project root (`../.env`).

## API

- `POST /api/auth/register` · `POST /api/auth/login`
- Teacher upload/process · Student lessons/chat/quiz/profile

## Database migrations

```bash
alembic upgrade head
```

## Clean demo data (one-time)

```bash
python scripts/purge_demo_data.py --audit   # list demo rows
python scripts/purge_demo_data.py           # delete demo rows
```

Removes all `*@eduspark.sy` accounts and legacy seeded teachers (e.g. أحمد الحسين، كريم العلي).

Optional reference subjects only (no demo users):

```bash
python scripts/seed_reference_subjects.py
```
