# Deployment Documentation

> AI 协作：环境/命令变更时更新本文件与 `workflows/debug-workflow.md` 常见问题。

This document describes local, build, test, and deployment workflows for Intel Hub. Production details are待补充 until the hosting target is selected.

## Environment Requirements

- Windows PowerShell for the primary local workflow.
- Python 3.11+.
- Node.js compatible with Next.js 14.
- Docker and Docker Compose.
- PostgreSQL 16.
- Redis 7.
- Optional OpenAI API key for real AI mode.

## Required Environment Files

- Root `.env` for Docker Compose defaults, based on `.env.example`.
- `backend/.env`, based on `backend/.env.example`.
- `apps/web/.env.local`, based on `apps/web/.env.example`.

Do not commit real local env files.

## Install Dependencies

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub
.\scripts\setup.ps1
```

If setup scripts fail, install backend and frontend dependencies manually using the commands documented in the relevant package files. Manual fallback details are待补充.

## Local Startup

Start infrastructure:

```powershell
docker compose up -d db redis
```

Run migrations:

```powershell
cd backend
$env:PYTHONPATH="C:\Users\sanford\Desktop\ai_code_new\intel-hub"
alembic upgrade head
cd ..
```

Start services in separate terminals:

```powershell
.\scripts\dev.ps1 backend
.\scripts\dev.ps1 worker
.\scripts\dev.ps1 beat
.\scripts\dev.ps1 frontend
```

## Build

Frontend:

```powershell
cd apps\web
npm run build
```

Docker:

```powershell
docker compose build
```

## Test

Backend:

```powershell
cd backend
$env:PYTHONPATH="C:\Users\sanford\Desktop\ai_code_new\intel-hub"
python -m pytest tests/ -q
```

Frontend:

```powershell
cd apps\web
npm run type-check
npm run build
```

Docker config:

```powershell
docker compose config
```

## Project Validation

One-shot local/dev validation script:

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub
.\scripts\validate_project.ps1
```

Quick mode (skip frontend production build):

```powershell
.\scripts\validate_project.ps1 -Quick
```

| Flag | Effect |
| --- | --- |
| `-SkipDocker` | Skip `docker compose config` |
| `-SkipBackend` | Skip backend pytest |
| `-SkipFrontend` | Skip frontend type-check and build |
| `-Quick` | Skip `npm run build` |

Exit code `0` = all executed checks passed; non-zero = at least one failure.

## Daily Operations

Owner-facing one-pager: **`docs/OWNER.md`**.

One-shot ingest → analyze → briefing (requires API + Celery Worker):

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub
.\scripts\run-daily-intel.ps1
```

Options: `-SkipIngest`, `-SkipAnalyze`, `-SkipBriefing`, `-IngestLimit 20`.

Open **http://localhost:3000/briefing** after Worker finishes queued tasks (1–3 min).

## Docker Compose Deployment

Development or staging:

```powershell
docker compose up -d
docker compose logs -f
docker compose up -d --build
docker compose down
```

Remove volumes only when intentional:

```powershell
docker compose down -v
```

## Individual Service Images

Backend:

```powershell
docker build -f docker/backend/Dockerfile -t intel-hub-backend .
docker run -p 8000:8000 --env-file backend/.env intel-hub-backend
```

Frontend:

```powershell
docker build -f docker/frontend/Dockerfile -t intel-hub-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 intel-hub-frontend
```

Worker:

```powershell
docker build -f docker/worker/Dockerfile -t intel-hub-worker .
docker run --env-file backend/.env intel-hub-worker
```

## Deployment Checklist

- [ ] Set `APP_ENV=production`.
- [ ] Set `APP_DEBUG=false`.
- [ ] Generate a secure `SECRET_KEY`.
- [ ] Configure `CORS_ORIGINS`.
- [ ] Configure real `DATABASE_URL`.
- [ ] Configure Redis broker/result backend.
- [ ] Configure `OPENAI_API_KEY` or explicitly document mock mode.
- [ ] Run migrations.
- [ ] Configure SSL/TLS termination.
- [ ] Configure log aggregation.
- [ ] Configure database backups.
- [ ] Configure worker and beat process supervision.
- [ ] Run backend tests.
- [ ] Run frontend type-check and build.

## Common Issues

| Issue | Likely Cause | Fix |
| --- | --- | --- |
| Backend cannot import `workers` or `services` | Missing repo root in `PYTHONPATH` | Set `PYTHONPATH` to repo root |
| AI analysis uses mock | `OPENAI_API_KEY` is empty | Configure key or accept mock mode |
| Worker does not process tasks | Redis not running or broker URL mismatch | Start Redis and check env vars |
| Worker slow to start on Windows | Default prefork pool | Use `.\scripts\dev.ps1 worker` (solo pool) |
| API hangs during batch ingest | Sync ingest in API process | Use `?async=1` or `batch-ingest-rss.py --async` |
| Frontend cannot reach API | `NEXT_PUBLIC_API_URL` mismatch | Update frontend env |
| Docker prompt loading fails | `PROMPTS_DIR` wrong | Use `/app/prompts` in Docker |

## Production Target

待补充.
