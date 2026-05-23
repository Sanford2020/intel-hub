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

### Authentication bootstrap (M6)

Set in `backend/.env` before first deploy:

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | HS256 JWT signing secret — **rotate in production** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL (default 60) |
| `INITIAL_ADMIN_EMAIL` | First admin email — bootstrapped on first successful login only |
| `INITIAL_ADMIN_PASSWORD` | First admin password — change after first login |

First-login checklist:

1. Set strong `SECRET_KEY` and `INITIAL_ADMIN_*` in production env.
2. Run `alembic upgrade head` (creates `users` / `user_sessions`).
3. Open `/login` and sign in with `INITIAL_ADMIN_*` credentials (creates admin row if DB is empty).
4. Create operator/analyst users via `POST /api/v1/auth/users` (admin Bearer token) or repeat bootstrap pattern in staging only.
5. Run `python scripts/acceptance-smoke.py --api http://127.0.0.1:8001` with `SMOKE_EMAIL` / `SMOKE_PASSWORD` matching your admin account.

Scripts (`seed-sources.py`, `acceptance-smoke.py`) authenticate via `POST /api/v1/auth/login` using `SMOKE_EMAIL` / `SMOKE_PASSWORD` (defaults: `admin@example.com` / `change-me`).

JWT rotation: update `SECRET_KEY`, restart API, and have all users re-login (existing tokens invalidate immediately).

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

One-shot local/dev validation script on Windows:

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

Linux/macOS equivalent:

```bash
cd /path/to/intel-hub
bash scripts/validate_project.sh
```

Quick mode:

```bash
bash scripts/validate_project.sh --quick
```

| Flag | Effect |
| --- | --- |
| `--skip-docker` | Skip `docker compose config` |
| `--skip-backend` | Skip backend pytest |
| `--skip-frontend` | Skip frontend type-check and build |
| `--quick` | Skip `npm run build` |

`make ci` is a bash-friendly wrapper for `scripts/validate_project.sh`.

## CI / Validate

GitHub Actions workflow: `.github/workflows/ci.yml`.

The CI job runs on `push` and `pull_request` to `main` and validates:

- PostgreSQL 16 and Redis 7 service containers are healthy.
- Backend dependencies install from `backend/requirements.txt`.
- Database migrations run with `alembic upgrade head`.
- Backend tests pass with `python -m pytest tests/ -q`.
- Frontend dependencies install with `npm ci`.
- Frontend type-check passes with `npm run type-check`.
- Frontend production build passes with `npm run build`.
- Docker Compose config renders with `docker compose config`.
- `bash scripts/validate_project.sh --quick` passes.

CI uses dummy/mock values for secrets such as `OPENAI_API_KEY` and `FEISHU_WEBHOOK_URL`; real production secrets must be configured in the deployment target, not in the workflow.

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
- [ ] Generate a secure `SECRET_KEY` (JWT signing; rotate with planned re-login window).
- [ ] Set `INITIAL_ADMIN_EMAIL` / `INITIAL_ADMIN_PASSWORD` for first bootstrap login.
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
