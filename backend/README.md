# Intel Hub Backend

FastAPI backend for Intel Hub.

## Responsibilities

- `/api/v1/sources`: source management, bulk import, RSS ingest trigger, ingest logs.
- `/api/v1/articles`: article CRUD, filtering, AI analysis, intelligence report lookup.
- `/api/v1/alerts`: keyword alert rules, alert events, rule evaluation.
- `/api/v1/stats/overview`: dashboard counts.
- `/api/v1/ai`: chat and prompt listing.
- `/api/v1/agents`: 12-factor agent runtime.

## Setup

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub
.\scripts\setup.ps1
```

Or install backend dependencies directly:

```powershell
cd backend
pip install -r requirements.txt
```

## Environment

Copy `backend/.env.example` to `backend/.env`.

Important values:

- `DATABASE_URL`: PostgreSQL connection.
- `REDIS_URL`: Redis connection.
- `CELERY_BROKER_URL`: Celery broker.
- `CELERY_RESULT_BACKEND`: Celery result backend.
- `OPENAI_API_KEY`: optional; empty means real OpenAI analysis is not enabled.
- `PROMPTS_DIR`: prompt template directory. In Docker this should be `/app/prompts`.

## Migrations

```powershell
cd backend
$env:PYTHONPATH="C:\Users\sanford\Desktop\ai_code_new\intel-hub"
alembic upgrade head
```

## Run

```powershell
.\scripts\dev.ps1 backend
```

From `backend/` directly:

```powershell
$env:PYTHONPATH="C:\Users\sanford\Desktop\ai_code_new\intel-hub"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Workers

```powershell
.\scripts\dev.ps1 worker
.\scripts\dev.ps1 beat
```

On Windows the worker launcher uses Celery `--pool solo`.

## Test

```powershell
cd backend
$env:PYTHONPATH="C:\Users\sanford\Desktop\ai_code_new\intel-hub"
python -m pytest tests/ -q
```

## API Contract

See `docs/api.md`.
