# Decisions Archive (Bootstrap Notes)

> **Superseded.** Architecture Decision Records (ADRs) live in the repository root [`DECISIONS.md`](../../DECISIONS.md).
> This file preserves early bootstrap notes previously in `docs/decisions.md` for link stability.

## 2026-05-19: Adopt `.multi-agent/` For Coordination

Intel Hub uses `.multi-agent/` for task cards, handoffs, role definitions, and review checklists.

Reason:

- The project is now mature enough for parallel agent work.
- The Commercial Edition has several independent lanes: frontend UX, backend workers, QA/release, docs/API contracts.
- Keeping coordination files inside the repo makes handoff state visible to future agents.

## 2026-05-19: Keep Current Commercial Edition Stack

The project continues with Next.js, FastAPI, Celery, PostgreSQL, Redis, and OpenAI/mock analysis.

Reason:

- Existing backend tests pass.
- Existing frontend type-check passes.
- The architecture already matches the product flow: collect, store, analyze, search, alert.

## 2026-05-19: Treat Local `.env` Files As Expected But Untracked

`backend/.env` and `apps/web/.env.local` may exist in local development, but must stay ignored and must not be committed.

Reason:

- Docker Compose and local scripts need local configuration.
- Real API keys and local secrets belong in ignored files.
- Example files are the source of truth for committed configuration.

## 2026-05-19: Use `/app/prompts` In Docker

Docker services set `PROMPTS_DIR=/app/prompts`, and backend/worker images copy the `prompts/` directory.

Reason:

- Local backend runs from `backend/`, where `../prompts` works.
- Docker runs from `/app`, where `../prompts` would resolve outside the application directory.
