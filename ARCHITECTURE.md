# ARCHITECTURE.md

This document summarizes the current Intel Hub architecture based on the repository structure. Unknowns are marked as `待补充`.

## System Purpose

Intel Hub is a Commercial Edition intelligence operations platform for collecting, normalizing, analyzing, searching, and alerting on multi-source information feeds.

## Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend API | FastAPI, Pydantic v2 |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Queue | Celery, Redis |
| AI | OpenAI API or mock fallback |
| Containers | Docker, Docker Compose |
| Tests | Pytest, Vitest, TypeScript type-check |

## Directory Structure

```text
apps/web/                 Next.js frontend
backend/app/              FastAPI application
backend/app/api/          API routing and dependencies
backend/app/modules/      Domain modules: sources, articles, ingest, intelligence, alerts
backend/app/models/       SQLAlchemy models
backend/app/db/           Async/sync database sessions and migrations
workers/                  Celery app and tasks
services/ai/              AI client, schemas, prompt helpers
services/agent/           Agent runtime helpers
packages/shared-types/    Shared TypeScript package
docker/                   Backend/frontend/worker Dockerfiles
scripts/                  Setup, dev, ingest, seed, migration helpers
  batch-ingest-rss.py     Batch RSS ingest (supports --async)
  backfill-source-urls.py Patch empty URLs from seeds
  parse-data-sources.py   Regenerate seeds from docs markdown
seeds/                    Source and Notion import seed data
docs/                     Product, architecture, deployment, API, and operations docs
prompts/                  Prompt templates and AI agent prompts
workflows/                AI development workflow docs
```

## Core Modules

| Module | Location | Responsibility |
| --- | --- | --- |
| Sources | `backend/app/modules/sources/` | Source CRUD, filters, source metadata |
| Articles | `backend/app/modules/articles/` | Article CRUD, filtering, detail, report lookup |
| Ingest | `backend/app/modules/ingest/`, `workers/tasks/ingest/` | RSS parsing, article creation, ingest logs |
| Intelligence | `backend/app/modules/intelligence/`, `workers/tasks/analyze/` | AI/mock summary, tags, entities, relevance |
| Alerts | `backend/app/modules/alerts/`, `workers/tasks/alerts/` | Keyword rules, alert events, notification stubs |
| Stats | `backend/app/api/v1/endpoints/stats.py` | Dashboard overview counts |
| Frontend | `apps/web/src/app/` | Dashboard, sources, articles, article detail, alerts |

## Data Flow

```text
Source definitions
  -> RSS ingest task
  -> Article storage and deduplication
  -> AI intelligence analysis
  -> Alert rule evaluation
  -> Alert event / notification stub
  -> Dashboard and article views
```

## External Dependencies

- PostgreSQL for persistent storage.
- Redis for Celery broker/result backend.
- OpenAI API when `OPENAI_API_KEY` is configured.
- RSS feeds and external source URLs.
- Optional webhook targets for alert notifications.
- Docker runtime for containerized local/staging execution.

## API Shape

Application routes are under `/api/v1`. Current REST areas:

- `/health`, `/ping`
- `/stats/overview`
- `/sources`
- `/articles`
- `/alerts`
- `/ai`
- `/agents`

See `docs/api.md` for details.

## Deployment Shape

Docker Compose defines:

- `db`
- `redis`
- `backend`
- `frontend`
- `worker`
- `beat`

See `docs/deployment.md` for details.

## Current Test Coverage

- Backend tests exist under `backend/tests/`.
- Frontend utility tests exist under `apps/web/__tests__/`.
- Full commercial runtime observation is still待补充.

## Operational Notes (Observed)

- `POST /api/v1/sources/{id}/ingest?async=true` queues Celery ingest without blocking API.
- Sync ingest runs in API process and can block other requests during large batch runs.
- Celery on Windows uses `--pool solo` via `scripts/dev.ps1`.
- Analyze/alerts tasks must be imported in `workers/tasks/*/__init__.py` for autodiscovery.

## Pending Questions

- Commercial authentication and authorization scope is待补充.
- Production hosting target is待补充.
- Rate limiting policy is待补充.
- Backup and retention policy is待补充.
- Real AI model/provider configuration strategy is待补充.
- Long-running worker/beat observation evidence is待补充.
