# REVIEW.md

This file records initial project risks for follow-up. Per initialization rules, no business code was changed to fix these items.

## Architecture Risks

- Commercial authentication and authorization are not yet defined in the current architecture docs.
- Production hosting target is not confirmed.
- Worker/beat 24-hour observation is not recorded, so long-running operational reliability remains unproven.
- Existing documentation exists in multiple locations (`PROJECT_BRIEF.md`, `docs/project/*`, `.multi-agent/*`), which can drift unless one source of truth is maintained.

## Code Quality Risks

- Repository currently appears to have many untracked files; baseline commit strategy should be clarified before multi-agent work.
- Some generated/runtime files appear near source areas, such as Celery beat schedule artifacts under `backend/`; confirm `.gitignore` coverage before committing.
- AI/mock behavior is useful for local development, but commercial behavior should clearly distinguish mock mode from real AI mode.

## Test Risks

- Backend tests pass in the current local environment; `scripts/validate_project.sh` and GitHub Actions CI now capture production-like checks (OPS-02).
- Frontend type-check/build pass, but end-to-end browser tests are not formalized.
- Worker/beat unattended runtime observation is pending.

## Documentation Risks

- ~~Root `DECISIONS.md` now exists, while `docs/decisions.md` also exists~~ **Resolved (ADR-20260521-03):** root `DECISIONS.md` is authoritative; `docs/decisions.md` is redirect only.
- API docs are manually maintained and may drift from FastAPI routers if not checked during review — **M5-D must sync `docs/api.md` for archives endpoints.**
- Deployment docs need production-specific values once hosting target is selected.

## Deployment Risks

- Docker Compose depends on local env files; fresh setup must copy examples correctly.
- No production secrets management strategy is documented yet.
- Backup, monitoring, alerting, and log aggregation are checklist items but not implemented in docs.

## AI Collaboration Risks

- Multiple AI tools may edit overlapping files unless `TASKS.md` ownership is kept current — **M5 implementation landed before M5-M Accepted; enforce ADR-before-code for future sprints.**
- **M5 + M5.5 parallel file boundaries:** `AppNav.tsx` / `archives/**` / `trends/**` — F1 must not touch archives; F2 only after M5-C REVIEW → DONE.
- Cursor, Windsurf, and Codex need clear prompts and review gates to avoid broad refactors.
- Structural issues should be recorded here first instead of silently fixed during unrelated tasks.
- `prompts/` contains both runtime YAML templates and AI-agent Markdown prompts; do not confuse the two.

## Commercial Delivery Risks (2026-05-22)

- **M5 sign-off gap:** M5-A/B/C in REVIEW; M5-D (Codex) not run — Commercial Edition cannot claim archive feature DONE until pytest + acceptance + `docs/api.md` sync.
- **Mock AI default:** empty `OPENAI_API_KEY` → `ai_mode=mock`; commercial demos must disclose; M7-C (cost guard) recommended before public deploy.
- **Auth undefined (M6):** no login/RBAC — do not expose dashboard publicly until S3 complete.
- **Archive backfill depth:** trends UX needs ≥7 days backfill; ops must run `backfill-archives.py --days 30` after deploy.
- **Dev port hygiene:** stale listeners on :8000 can serve pre-M5 backend; standardize on :8001 per `dev.ps1` until resolved.

## M5-D Archive Review (2026-05-22)

Verdict: **BLOCK** — M5 archive-specific tests pass and API docs are now synced, but M5-D cannot move M5-A/B/C to DONE because required root `pytest -q` failed and live acceptance smoke could not reach a running API.

### Findings

- **P0: Required validation command `pytest -q` fails from repo root.** Result: 27 failed, 53 passed, 76 warnings. Main failure classes: `backend/tests/test_ai.py` cannot find `default` prompt when run from root; multiple API tests receive `async_generator` instead of `AsyncSession`, e.g. `backend/tests/test_archives.py::test_category_heat_trends_api`, alerts, articles, briefings, intelligence, sources. The project PowerShell validation still passes because it runs from `backend`.
- **P1: Archive failure semantics do not match M5-D acceptance note.** `create_or_update_daily_archive_sync()` writes `status="failed"` and re-raises when briefing/metrics fail; M5-D requested upstream briefing failure -> archive `status="partial"` and task not hanging. This is non-trivial business behavior, so Codex did not patch it.
- **P2: Review evidence gaps remain for production-like archive operation.** `briefing_json` p95 size and metrics SQL `EXPLAIN` were not measured because no live archive rows/API database were available. Local API ports 8000/8001 refused connection; `scripts/acceptance-smoke.py --api http://127.0.0.1:8001` failed at health.

### Verification

- `python -m pytest tests/test_archives.py -q` from `backend`: **PASS**, 5 passed.
- `powershell -ExecutionPolicy Bypass -File scripts/validate_project.ps1 -Quick -SkipDocker`: **PASS**, backend pytest 80 passed, frontend type-check PASS.
- `pytest -q` from repo root: **FAIL**, 27 failed / 53 passed.
- Archive API coverage: **PASS via TestClient tests** for `/api/v1/archives`, `/api/v1/archives/{date}`, `/api/v1/archives/trends/category-heat`.
- `docs/api.md`: **UPDATED** with archives/trends contract.

### Review Notes

- Backend implementation includes `daily_archives` model/migration, archive metrics, service, router, and UTC 06:15 Celery Beat task.
- Frontend includes `/archives`, `/archives/{date}`, `/trends`, TS types, and `intel-api.ts` wrappers.
- M5-D should be rerun after the root pytest environment/fixture issue is resolved and a seeded API is available for acceptance smoke.

## Operational Risks (Sprint 6 Observations)

- **Sync batch ingest blocks API** for minutes when many RSS sources are ingested synchronously; use `?async=1` or `batch-ingest-rss.py --async`.
- ~~**Many Tier-0 RSS feeds fail** from local network (BBC/CNN timeout, Reuters 404, AP invalid XML)~~ **OPS-01 probed 2026-05-22:** `docs/operations/rss-health-2026-05.md` generated; failed enabled RSS rows were marked `enabled=false` in seeds. Remaining risk: results are localnet-only and RSSHub X requires a running local RSSHub service, so production/staging should rerun the probe before permanent source removal.
- **Celery Worker/Beat are not always running** in dev; articles/reports will not grow without them.
- **Worker autodiscovery** previously missed analyze/alerts tasks when `__init__.py` did not import modules; regression risk if new task packages omit imports.
- **Mock AI mode** is active when `OPENAI_API_KEY` is empty; commercial demos must label mock vs real output.

## Context Risks

- Long chat sessions without TASK updates lose Scope boundaries.
- Pasting full worker logs into Master context reduces planning quality.
- Duplicate docs (`ARCHITECTURE.md` / `docs/architecture.md`) — ADR path resolved via ADR-20260521-03.
- `prompts/` mixes runtime YAML (AI analysis) with Skill Markdown — agents must not edit YAML during bootstrap tasks.

## Long-term Maintenance Risks

- No formal E2E browser suite.
- RSS feed list requires ongoing curation as URLs rot.
- Commercial auth undefined — security model incomplete.
- Production hosting target unknown.

## Follow-up Recommendations

- ~~Create a validation script task.~~ Done: OPS-02 (`validate_project.sh` + CI).
- Create a commercial auth architecture task — M6-ADR pending (S3).
- Record a worker/beat observation task — OPS-03 pending.
- ~~Decide whether root `DECISIONS.md` supersedes `docs/decisions.md`.~~ Done: ADR-20260521-03.
