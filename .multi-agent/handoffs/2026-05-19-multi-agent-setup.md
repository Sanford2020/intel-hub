# Handoff: Multi-Agent Setup

## Done

- Installed `.multi-agent/` workflow assets from `multi-agent-dev-kit`.
- Filled `PROJECT_BRIEF.md` for Intel Hub.
- Replaced `.multi-agent/sprint.md` with Sprint 6 operational hardening plan.
- Added task cards for docs, release readiness, worker observation, and frontend UX hardening.
- Captured baseline verification.
- Fixed frontend API handling for empty/204 responses and non-JSON error bodies.
- Removed duplicate article filter loads and added invalid article ID handling.
- Added Intel Hub API contract, backend README, Windows local dev guide, decision log, and Sprint 6 operations runbook.
- Fixed root `.env.example` database naming.
- Added `.dockerignore`.
- Set Docker `PROMPTS_DIR=/app/prompts` for backend/worker/beat and copied `prompts/` into worker image.
- Switched backend/worker Dockerfiles to install from `backend/requirements.txt`, avoiding stale Poetry lock during Docker builds.

## Changed

- `PROJECT_BRIEF.md`
- `.multi-agent/sprint.md`
- `.multi-agent/task-cards/TASK-001-operational-docs.md`
- `.multi-agent/task-cards/TASK-002-env-and-release-readiness.md`
- `.multi-agent/task-cards/TASK-003-worker-observation.md`
- `.multi-agent/task-cards/TASK-004-frontend-ux-hardening.md`
- `.multi-agent/handoffs/2026-05-19-multi-agent-setup.md`
- `.dockerignore`
- `.env.example`
- `README.md`
- `docs/api.md`
- `docs/local-dev-windows.md`
- `docs/decisions.md`
- `docs/operations/Sprint-6-runbook.md`
- `backend/README.md`
- `backend/pyproject.toml`
- `docker-compose.yml`
- `docker/backend/Dockerfile`
- `docker/worker/Dockerfile`
- `apps/web/.eslintrc.json`
- `apps/web/src/lib/api.ts`
- `apps/web/src/app/articles/page.tsx`
- `apps/web/src/app/articles/[id]/page.tsx`
- `apps/web/src/stores/theme.ts`

## Verified

```text
cd backend
python -m pytest tests/ -q
Result: 31 passed

cd apps/web
npm run type-check
Result: passed

cd apps/web
npm run build
Result: passed

docker compose config --quiet
Result: passed
```

## Risks

- Real `backend/.env` exists locally and must remain ignored.
- Sprint 6 still needs a real 24h worker/beat observation.
- OpenAI real-analysis mode depends on `OPENAI_API_KEY`.
- `poetry.lock` does not contain newly declared `asyncpg` and `aiosqlite`; refresh it later in an environment with working Poetry.
- `docker compose build backend worker` could not complete because Docker Hub auth/metadata fetch timed out before build layers ran.
- The generic validation script flags local ignored env files and example secret text inside synced agency docs; treat as security reminders, not committed-file failures.

## Next

- QA/Release Agent should finish environment/readiness cleanup.
- Backend Agent should run worker/beat observation.
- Frontend Agent should do route-level UX hardening.
