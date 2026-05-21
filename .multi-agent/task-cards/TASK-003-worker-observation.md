# TASK-003: Worker And Beat Observation

## Task Info

- Type: backend / operations
- Priority: P1
- Status: pending
- Owner: Backend Agent

## Goal

Prove the ingestion -> analysis -> alert loop can run unattended long enough to be trusted as a daily workflow.

## Allowed Changes

| Path | Purpose |
| --- | --- |
| `workers/**` | Celery task registration or queue fixes |
| `backend/app/modules/**` | Service-level fixes uncovered by observation |
| `backend/tests/**` | Regression tests |
| `docs/project/**` | Observation notes |
| `docs/operations/**` | Runbooks and observation logs |

## Acceptance Criteria

- Worker starts with Windows-safe solo pool.
- Beat schedules ingestion/analyze/alert tasks as expected.
- 24h observation records: start time, source count, created articles, analyzed reports, alert events, failures.
- Any recurring failure has a task card or test.

## Suggested Commands

```powershell
docker compose up -d db redis
.\scripts\dev.ps1 worker
.\scripts\dev.ps1 beat
python scripts\batch-ingest-rss.py --async
```

## Verification

- `python -m pytest tests/test_e2e_ingest_analyze.py -q`
- Manual check of `/api/v1/stats/overview`

## Runbook

See `docs/operations/Sprint-6-runbook.md`.
