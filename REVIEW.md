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

- Backend tests pass in the current local environment, but production-like Docker validation is not yet captured in a standard validation script.
- Frontend type-check/build pass, but end-to-end browser tests are not formalized.
- Worker/beat unattended runtime observation is pending.

## Documentation Risks

- Root `DECISIONS.md` now exists, while `docs/decisions.md` also exists; future agents should avoid divergent ADR records.
- API docs are manually maintained and may drift from FastAPI routers if not checked during review.
- Deployment docs need production-specific values once hosting target is selected.

## Deployment Risks

- Docker Compose depends on local env files; fresh setup must copy examples correctly.
- No production secrets management strategy is documented yet.
- Backup, monitoring, alerting, and log aggregation are checklist items but not implemented in docs.

## AI Collaboration Risks

- Multiple AI tools may edit overlapping files unless `TASKS.md` ownership is kept current.
- Cursor, Windsurf, and Codex need clear prompts and review gates to avoid broad refactors.
- Structural issues should be recorded here first instead of silently fixed during unrelated tasks.
- `prompts/` contains both runtime YAML templates and AI-agent Markdown prompts; do not confuse the two.

## Operational Risks (Sprint 6 Observations)

- **Sync batch ingest blocks API** for minutes when many RSS sources are ingested synchronously; use `?async=1` or `batch-ingest-rss.py --async`.
- **Many Tier-0 RSS feeds fail** from local network (BBC/CNN timeout, Reuters 404, AP invalid XML); operational value depends on feed curation.
- **Celery Worker/Beat are not always running** in dev; articles/reports will not grow without them.
- **Worker autodiscovery** previously missed analyze/alerts tasks when `__init__.py` did not import modules; regression risk if new task packages omit imports.
- **Mock AI mode** is active when `OPENAI_API_KEY` is empty; commercial demos must label mock vs real output.

## Context Risks

- Long chat sessions without TASK updates lose Scope boundaries.
- Pasting full worker logs into Master context reduces planning quality.
- Duplicate docs (`ARCHITECTURE.md` / `docs/architecture.md`, two DECISIONS paths) increase drift.
- `prompts/` mixes runtime YAML (AI analysis) with Skill Markdown — agents must not edit YAML during bootstrap tasks.

## Long-term Maintenance Risks

- No formal E2E browser suite.
- RSS feed list requires ongoing curation as URLs rot.
- Commercial auth undefined — security model incomplete.
- Production hosting target unknown.

## Follow-up Recommendations

- Create a validation script task.
- Create a commercial auth architecture task.
- Record a worker/beat observation task.
- Decide whether root `DECISIONS.md` supersedes `docs/decisions.md`.
