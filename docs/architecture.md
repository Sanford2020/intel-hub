# Architecture Overview

## System Design

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend   │────▶│   Backend    │────▶│  Database   │
│  (Next.js)   │     │  (FastAPI)   │     │ (PostgreSQL) │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────┴───────┐
                    │    Redis     │
                    │ (Cache/Queue)│
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │   Workers    │
                    │  (Celery)    │
                    └──────────────┘
```

## Data Flow

1. **Client Request** → Frontend → Backend API → Service Layer → Database
2. **Background Task** → Backend → Redis Queue → Celery Worker → Result
3. **AI Processing** → Backend → AI Service → OpenAI API → Structured Response

## Module Dependencies

- `backend/app/` → Core application (FastAPI, API routes, models)
- `services/ai/` → AI client and prompt management (depends on `backend/app/config`)
- `workers/` → Background task processing (depends on `backend/app/config`)
- `packages/shared/` → Shared utilities (no dependencies)
- `packages/shared-types/` → TypeScript types shared with frontend
- `agents/` → Multi-Agent role definitions and orchestrator workflow
- `prompts/` → YAML prompt templates with structured JSON output schemas
- `config/` → Centralized configuration (re-exports from `backend/app/config`)

## Scaling Strategy

1. **Horizontal**: Scale backend and workers independently via Docker replicas
2. **Database**: Read replicas, connection pooling, eventual sharding
3. **Cache**: Redis cluster for high-availability caching
4. **Queue**: Separate queues by priority and task type
5. **Frontend**: CDN deployment with edge caching
