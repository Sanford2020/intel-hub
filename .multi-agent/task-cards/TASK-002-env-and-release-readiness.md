# TASK-002: Environment And Release Readiness

## Task Info

- Type: release / configuration
- Priority: P0
- Status: done
- Owner: QA/Release Agent

## Goal

Make a fresh developer or agent able to understand required environment variables, local services, and verification commands without reading hidden local state.

## Allowed Changes

| Path | Purpose |
| --- | --- |
| `.env.example` | Root Docker Compose defaults |
| `backend/.env.example` | Backend runtime defaults |
| `apps/web/.env.example` | Frontend runtime defaults |
| `README.md` | Setup and verification instructions |
| `scripts/**` | Safe setup/test helpers |

## Forbidden Changes

| Path | Reason |
| --- | --- |
| `backend/.env` | Real local secrets/config must stay untracked |
| `apps/web/.env.local` | Local developer config |
| `backend/app/**` | Not needed for release docs unless validation reveals a bug |

## Acceptance Criteria

- Root `.env.example` uses `intel_hub` database naming.
- README documents multi-agent workflow and validation commands.
- `python -m pytest tests/ -q` passes from `backend/`.
- `npm run type-check` passes from `apps/web/`.
- `.multi-agent` validation produces no required-document errors.

## Notes

Docker Compose currently reads `backend/.env` for backend, worker, and beat containers. Fresh setup should copy from `backend/.env.example`.

## Completion Notes

- Root `.env.example` now uses `intel_hub`.
- Docker services set `PROMPTS_DIR=/app/prompts`.
- Worker image copies `prompts/`.
- `.dockerignore` excludes local secrets, caches, node modules, build output, and celery beat state.
- Remaining caveat: `poetry.lock` still needs refresh in an environment with a working Poetry installation after adding `asyncpg` and `aiosqlite` to `backend/pyproject.toml`.
- Docker backend/worker images now install from `backend/requirements.txt`, which already contains the async database drivers.
