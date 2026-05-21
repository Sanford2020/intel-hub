# Intel Hub Multi-Agent Sprint

## Sprint 6: Operational Hardening

Status: in progress

Goal: turn the Commercial Edition baseline into a reproducible daily intelligence workflow with clear agent ownership, reliable worker commands, and release-ready checks.

## Active Agent Lanes

| Lane | Agent | Scope | Current output |
| --- | --- | --- | --- |
| A | Architect / Planner | Project brief, sprint plan, task cards, handoff protocol | `.multi-agent/`, `PROJECT_BRIEF.md` |
| B | Frontend | Next.js dashboard, typed API client, route UX | `apps/web/src/**` |
| C | Backend / Worker | FastAPI, Celery tasks, ingestion/analyze/alert loop | `backend/**`, `workers/**` |
| D | QA / Release | Env examples, scripts, Docker, validation | `scripts/**`, `docker/**`, env examples |

## Current Sprint Tasks

| Task | Owner | Status | Verification |
| --- | --- | --- | --- |
| [TASK-001](task-cards/TASK-001-operational-docs.md) | Architect Agent | Done | Docs exist and match current commercial baseline/Sprint 6 |
| [TASK-002](task-cards/TASK-002-env-and-release-readiness.md) | QA/Release Agent | Done | Env examples and validation pass |
| [TASK-003](task-cards/TASK-003-worker-observation.md) | Backend Agent | Pending | Worker/beat 24h observation notes |
| [TASK-004](task-cards/TASK-004-frontend-ux-hardening.md) | Frontend Agent | Done | Type-check/build and route scan |

## Definition Of Done

- `PROJECT_BRIEF.md` reflects the actual Intel Hub product and current sprint.
- `.multi-agent/` contains roles, sprint, task cards, handoff templates, and review checklists.
- Root `.env.example` and `backend/.env.example` are consistent with `intel_hub`.
- Backend tests pass.
- Frontend type-check passes.
- Remaining Sprint 6 work is explicit, assigned, and verifiable.

## Latest Verification

```text
2026-05-19
- Backend: python -m pytest tests/ -q -> 31 passed
- Frontend: npm run type-check -> passed
```
