# Intel Hub Project Brief

## 1. Project Overview

- Project name: Intel Hub
- Project code: intel-hub
- Current phase: Commercial Edition hardening; core intelligence workflow implemented, commercial readiness in progress
- Owner: Sanford
- Main collaborators: Product/Architect Agent, Frontend Agent, Backend/Worker Agent, QA/Release Agent
- Created: 2026-05-19
- Last updated: 2026-05-19

## 2. One-Line Goal

Intel Hub is a global intelligence and news operations hub for collecting, normalizing, analyzing, searching, and alerting on multi-source information feeds.

## 3. Background And Motivation

- Current problem: global intelligence sources are fragmented across RSS, sites, APIs, notes, and manual monitoring workflows.
- Existing state: Commercial Edition baseline already includes source management, RSS ingestion, article storage, AI/mock analysis, filtering, dashboard, and keyword alerts.
- Current opportunity: move from "feature complete" to "commercially reliable daily intelligence workflow".
- Risk of not improving: ingestion, worker, environment, and handoff knowledge stay dependent on local memory instead of reproducible project assets.

## 4. Target Users

| User type | Core need | Use case | Success standard |
| --- | --- | --- | --- |
| Researcher / analyst | Track global topics efficiently | Scan sources, filter articles, inspect summaries | Can find relevant new items without manual source hopping |
| Investor / strategist | Monitor industry and geopolitical signals | Follow selected feeds and alert keywords | Receives timely alerts for watched themes |
| Media / content operator | Build topic and素材池 | Use article list and intelligence summaries | Can turn monitored feeds into topic candidates |
| Small team | Share internal intelligence workflow | Use dashboard, sources, alerts, and reports | Workflow can run repeatedly with documented commands |

## 5. Scope

### Must include

- Source CRUD and enabled/tier/category filtering.
- RSS ingestion, deduplication, and ingest logs.
- Article list/detail, filtering, and report lookup.
- AI analysis with OpenAI when configured and mock fallback when not configured.
- Keyword alert rules and event history.
- Worker/beat commands for recurring ingestion and analysis.
- Multi-agent project workflow assets under `.multi-agent/`.

### Not in current sprint

- Multi-tenant accounts and permissions.
- Production authentication.
- Elasticsearch or advanced full-text search.
- Translation pipeline.
- Entity relationship graph.
- Mobile app or push notifications.

### Explicit non-goals

- Replacing the current FastAPI/Next.js architecture.
- Introducing a black-box agent framework.
- Committing real secrets or local `.env` files.

## 6. Core Deliverables

| Deliverable | Description | Owner | Verification |
| --- | --- | --- | --- |
| Commercial app | FastAPI + Next.js + Celery + PostgreSQL/Redis workflow | Integration Agent | Backend tests and frontend type/build checks |
| Operational docs | Project brief, sprint plan, task cards, handoff protocol | Architect Agent | Files exist and match current sprint |
| Worker reliability | Ingest/analyze/alert queue paths are documented and testable | Backend Agent | Pytest plus smoke command |
| Dashboard UX | Source/article/alert flows stay usable in dev | Frontend Agent | Type-check/build and manual route scan |
| Release readiness | Env examples, compose config, validation script are consistent | QA/Release Agent | `validate_project.ps1`, tests, build |

## 7. Multi-Agent Assignment

| Agent | Scope | Writable paths | Avoid |
| --- | --- | --- | --- |
| Architect Agent | Planning, task cards, handoff, architecture decisions | `PROJECT_BRIEF.md`, `.multi-agent/**`, `docs/project/**` | Business logic without explicit task |
| Frontend Agent | Next.js dashboard and typed API client | `apps/web/src/**`, `apps/web/package.json` | Backend API semantics without contract update |
| Backend Agent | FastAPI modules, workers, migrations, tests | `backend/app/**`, `backend/tests/**`, `workers/**`, `services/**` | Frontend UI implementation |
| QA/Release Agent | Scripts, env examples, compose, validation | `scripts/**`, `.env.example`, `backend/.env.example`, `docker-compose.yml`, `docker/**` | Feature behavior changes without tests |

## 8. Technical Constraints

- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS.
- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic v2.
- Queue: Celery + Redis.
- Storage: PostgreSQL.
- AI: OpenAI API or mock mode.
- API prefix: `/api/v1/`.
- Local OS priority: Windows PowerShell commands must work.
- Secrets: only placeholder values in examples; real `.env` files stay ignored.

## 9. Ownership Map

| Path | Purpose | Owner | Rule |
| --- | --- | --- | --- |
| `apps/web/` | Dashboard frontend | Frontend Agent | Keep strict TypeScript passing |
| `backend/app/` | API and domain modules | Backend Agent | Route handlers stay thin; service logic in modules |
| `workers/` | Celery tasks | Backend Agent | Task names must stay registered and documented |
| `services/` | AI and agent runtime helpers | Backend/Architect Agent | Structured JSON at AI/agent boundaries |
| `docs/project/` | Project product and architecture docs | Architect Agent | Update when scope or architecture changes |
| `.multi-agent/` | Multi-agent operating system | Architect/QA Agent | Append task/handoff records; avoid overwriting active work |
| `scripts/` | Setup, dev, sync, test helpers | QA/Release Agent | Scripts must be safe and documented |

## 10. Milestones

| Milestone | Goal | Owner | Status |
| --- | --- | --- | --- |
| M1 | Commercial Edition baseline feature completion | Integration Agent | Done |
| M2 | Sprint 6 ingestion/analyze/alert loop operational | Backend Agent | In progress |
| M3 | Multi-agent workflow assets installed | Architect Agent | Done |
| M4 | Release readiness and 24h observation notes | QA/Release Agent | Pending |

## 11. Acceptance Criteria

- Backend tests pass with `python -m pytest tests/ -q` from `backend/`.
- Frontend type-check passes with `npm run type-check` from `apps/web/`.
- Project has current `PROJECT_BRIEF.md`, `.multi-agent/sprint.md`, and task cards.
- Environment examples use Intel Hub names and placeholder values.
- README points developers to the multi-agent workflow.
- Any incomplete operational work is represented as a task card with owner, scope, and verification.

## 12. Risks And Dependencies

| Risk / dependency | Impact | Mitigation | Owner |
| --- | --- | --- | --- |
| Missing `OPENAI_API_KEY` | AI analysis runs in mock mode | Document mock vs real AI mode clearly | QA/Release Agent |
| Long-running beat/worker not observed for 24h | Operational reliability not proven | Add Sprint 6 observation task | Backend Agent |
| Local `.env` exists but is ignored | Validation tools may flag it | Keep ignored; never commit real secrets | QA/Release Agent |
| Docker expects `backend/.env` | Fresh clone may fail before setup | Document setup and keep `backend/.env.example` current | QA/Release Agent |

## 13. Communication Rules

- Each agent declares role, scope, files owned, files avoided, verification, and handoff target before editing.
- Shared API/schema changes require docs or type updates in the same task.
- If two agents need the same file, one owns the edit and the other submits notes or waits for handoff.
- Every completed task reports: changed files, verification result, risks, and next step.

## 14. Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-19 | Use `.multi-agent/` as the local coordination system | Keeps multi-agent task state inside the repo without changing runtime code |
| 2026-05-19 | Keep Commercial Edition stack: Next.js + FastAPI + Celery + PostgreSQL + Redis | Existing tests pass and architecture already supports Sprint 6 |
