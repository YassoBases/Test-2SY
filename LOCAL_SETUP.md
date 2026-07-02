# EduSpark — Local setup checklist

Your error `password authentication failed for user "eduspark"` means PostgreSQL is running, but the **login role** in `.env` does not match your server.

The database `eduspark_syria` can exist while the user `eduspark` does not.

> **Note:** pgvector is **optional** (default `ENABLE_PGVECTOR=false`). You do not need
> the `vector` extension to run EduSpark. Only enable it if you set `ENABLE_PGVECTOR=true`.

## Option A — Use your existing `postgres` superuser (fastest)

1. Open project `.env` and set your real PostgreSQL password:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_ACTUAL_PASSWORD
POSTGRES_DB=eduspark_syria
```

2. Create the database (in pgAdmin or psql):

```sql
CREATE DATABASE eduspark_syria;
```

3. Create the schema and seed test users:

```powershell
cd backend
.\venv\Scripts\activate
alembic upgrade head
python scripts\seed_test_users.py
python scripts\verify_setup.py   # optional connectivity check
```

4. Start API:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

5. Open http://127.0.0.1:8000/docs

## Option B — Create dedicated `eduspark` user (matches setup_local_db.sql)

Run the bundled script as the `postgres` superuser:

```powershell
psql -U postgres -f backend\scripts\setup_local_db.sql
```

This creates the `eduspark_syria` database and the `eduspark` role. Keep `.env`:

```env
POSTGRES_USER=eduspark
POSTGRES_PASSWORD=eduspark
POSTGRES_DB=eduspark_syria
```

Then run `alembic upgrade head`, `python scripts\seed_test_users.py`, and start uvicorn.

## Verify everything

| Step | Command / URL |
|------|----------------|
| DB connection | `python scripts\verify_setup.py` |
| Create schema | `alembic upgrade head` |
| Seed test users | `python scripts\seed_test_users.py` |
| API health | http://127.0.0.1:8000/health |
| Swagger | http://127.0.0.1:8000/docs |
| Login test | `python scripts\test_api.py` |
| Frontend | `npm run dev` → http://localhost:5173 |

### Test accounts (after seed)

| Email | Password | Role |
|-------|----------|------|
| test.auth.student@eduspark-test.dev | TestOnly123! | student |
| test.auth.teacher@eduspark-test.dev | TestOnly123! | teacher |
| test.auth.parent@eduspark-test.dev | TestOnly123! | parent |

## Frontend API

Ensure root `.env` has:

```env
VITE_API_URL=http://localhost:8000
```

Vite proxies `/api` to the backend during `npm run dev`.
