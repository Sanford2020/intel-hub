# Sprint 6 Operations Runbook

Goal: observe the ingestion -> analysis -> alert loop long enough to trust Intel Hub as a repeatable daily workflow.

## Prerequisites

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub
.\scripts\setup.ps1
docker compose up -d db redis
```

Run migrations:

```powershell
cd backend
$env:PYTHONPATH="C:\Users\sanford\Desktop\ai_code_new\intel-hub"
alembic upgrade head
cd ..
```

Optional real AI mode:

```powershell
# Set in backend/.env
OPENAI_API_KEY=...
```

If `OPENAI_API_KEY` is empty, analysis should remain in mock/fallback mode.

## Start Services

Open separate terminals:

```powershell
.\scripts\dev.ps1 backend
.\scripts\dev.ps1 worker
.\scripts\dev.ps1 beat
.\scripts\dev.ps1 frontend
```

## Seed And Trigger

```powershell
python scripts\seed-sources.py
python scripts\batch-ingest-rss.py --async
```

## Observation Checklist

Record every observation cycle:

| Time | Sources enabled | Articles total | Reports total | Alert events | Failures |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

Check:

- Backend health: `http://localhost:8000/api/v1/health`
- Overview stats: `http://localhost:8000/api/v1/stats/overview`
- Dashboard: `http://localhost:3000`
- Worker terminal: no repeated task registration or import errors.
- Beat terminal: schedules ingestion/analyze tasks on expected intervals.

## Success Criteria

- Worker and beat remain running for the observation window.
- New RSS items are ingested or skipped with logs.
- Created articles are analyzed.
- Alert rules evaluate without crashing.
- Failures are explainable and have task cards.

## Recovery

- Empty database: run `alembic upgrade head`.
- Backend offline: restart `.\scripts\dev.ps1 backend`.
- Worker import error: verify `PYTHONPATH` points to repo root.
- Prompt loading error in Docker: verify `PROMPTS_DIR=/app/prompts`.
- Redis issue: `docker compose restart redis`.
