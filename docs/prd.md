# Product Requirements Document（产品需求文档）

> 协作：`AGENTS.md` · `SKILLS.md` · `TASKS.md` · 架构：`ARCHITECTURE.md`

## Project Goal

Intel Hub is a Commercial Edition intelligence operations platform for collecting, normalizing, analyzing, searching, and alerting on multi-source global information feeds.

## User Roles

| Role | Need |
| --- | --- |
| Researcher / Analyst | Track global topics and inspect AI summaries quickly |
| Investor / Strategist | Monitor geopolitical, market, and industry signals |
| Media / Content Operator | Build a reusable topic and source pool |
| Small Team | Share a repeatable intelligence workflow |
| Admin / Operator | Maintain sources, workers, env config, and alert rules |

## Core Scenarios

1. An operator imports and manages intelligence sources.
2. The system ingests RSS sources on schedule or manual trigger.
3. Articles are stored, deduplicated, and made searchable.
4. AI analysis generates summaries, tags, entities, and relevance.
5. Analysts filter articles and inspect detail pages.
6. Alert rules match keywords and create event history.
7. Operators monitor system status and counts from the dashboard.
8. Analysts open **Daily Briefing** (`/briefing`) for a ranked summary of the last 24h analyzed articles (Delivery Layer).
9. Operators receive the same briefing via **Feishu webhook** after the scheduled Celery job (optional `FEISHU_WEBHOOK_URL`).

## Functional Modules

| Module | Description | Current Status |
| --- | --- | --- |
| Source Management | CRUD, tier/category/enabled filtering | Implemented |
| RSS Ingestion | Manual and scheduled collection through Celery | Implemented |
| Article Repository | Storage, deduplication, list/detail/filtering | Implemented |
| AI Intelligence | Summary/tags/entities/relevance (0–10) with OpenAI or mock | Implemented |
| Alerting | Keyword rules, events, notification stubs | Implemented |
| **Daily Briefing** | Aggregated ranked digest API + `/briefing` page | Implemented |
| **Briefing Push** | Feishu interactive card after Beat / manual task | Implemented (env optional) |
| Dashboard | Overview stats and navigation | Implemented |
| Agent Runtime | 12-factor style agent run helpers | Present, details待补充 |
| Commercial Auth | Tenant/user/permission model | 待补充 |

## Non-Functional Requirements

- Reliability: worker/beat loop should run unattended and recover from transient failures.
- Observability: logs, alert events, ingest logs, and dashboard stats should make operations visible.
- Security: secrets must stay in ignored env files or managed secret stores.
- Maintainability: API contracts and frontend types must stay synchronized.
- Portability: local Windows PowerShell workflow and Docker Compose workflow should both work.
- Performance: article filtering and source listing should remain responsive as data grows.

## MVP Scope

For this commercial project, interpret MVP scope as the minimum commercial baseline:

- Source management.
- RSS ingestion.
- Article storage and deduplication.
- AI summary and tagging.
- Basic filtering and search.
- Keyword alert rules and event history.
- Dashboard overview.
- Worker/beat commands.
- Daily briefing page and API.
- Optional Feishu push for daily briefing.

## Out Of Scope For Now

- Multi-tenant accounts and permissions.
- Production authentication.
- Full-text search engine or advanced ranking.
- Translation pipeline.
- Entity graph UI.
- Mobile native app.
- Billing and subscription management.
- Email / Discord briefing channels (Feishu webhook only for push).

## Open Product Questions

- What is the first commercial user role to optimize for?
- Is authentication required before external users access the app?
- What notification channels are required beyond log/webhook/email stub?
- What source volume defines commercial readiness?
- What SLA or uptime target should guide deployment?
