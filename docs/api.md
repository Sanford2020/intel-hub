# API Documentation

> AI 协作：变更 API 时同步 `apps/web/src/types/` 与本文件。模板与规则见下文；端点列表基于当前 FastAPI 路由。

Base URL:

- Local API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

All application endpoints are under `/api/v1`.

## API Design Rules

- Use REST resource names under `/api/v1`.
- Keep query parameters explicit: `page`, `page_size`, `enabled`, `tier`, `source_id`, `q`.
- Keep backend schemas and frontend types synchronized.
- Use consistent pagination response shapes.
- Do not change endpoint behavior without updating this file.

## Response Shapes

Wrapped response:

```json
{
  "success": true,
  "data": {}
}
```

Paginated response:

```json
{
  "success": true,
  "data": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "total_pages": 0
}
```

Error response from app errors:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": {}
  }
}
```

FastAPI validation errors may still use FastAPI's default `detail` array. Standardizing all validation errors is待补充.

## Health

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/v1/health` | App health, version, environment, timestamp |
| GET | `/api/v1/ping` | Lightweight ping |

## Stats

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/v1/stats/overview` | Dashboard counts for sources, articles, reports, alert rules, alert events |

## Sources

| Method | Path | Query / Body | Notes |
| --- | --- | --- | --- |
| GET | `/api/v1/sources` | `page`, `page_size`, `category`, `tier`, `enabled` | Paginated source list |
| POST | `/api/v1/sources` | `SourceCreate` | Create source |
| POST | `/api/v1/sources/import` | `SourceBulkImportRequest` | Bulk import source definitions |
| GET | `/api/v1/sources/{source_id}` | None | Get source |
| PATCH | `/api/v1/sources/{source_id}` | `SourceUpdate` | Update source |
| DELETE | `/api/v1/sources/{source_id}` | None | Delete source, returns 204 |
| POST | `/api/v1/sources/{source_id}/ingest` | Query `async=true/false` | Queue or run RSS ingest |
| GET | `/api/v1/sources/{source_id}/ingest-logs` | `page`, `page_size` | Paginated ingest logs |

## Articles

| Method | Path | Query / Body | Notes |
| --- | --- | --- | --- |
| GET | `/api/v1/articles` | `page`, `page_size`, `source_id`, `tag`, `published_from`, `published_to`, `has_report`, `min_relevance` (0–10), `q` | Paginated article search; with `min_relevance`, only articles with reports meeting score are returned, ordered by score desc |
| POST | `/api/v1/articles` | `ArticleCreate` | Create article |
| GET | `/api/v1/articles/{article_id}` | None | Get article detail |
| PATCH | `/api/v1/articles/{article_id}` | `ArticleUpdate` | Update article |
| DELETE | `/api/v1/articles/{article_id}` | None | Delete article, returns 204 |
| POST | `/api/v1/articles/{article_id}/analyze` | None | Run AI/mock analysis and evaluate alerts |
| GET | `/api/v1/articles/{article_id}/report` | None | Get intelligence report |

## Alerts

| Method | Path | Query / Body | Notes |
| --- | --- | --- | --- |
| GET | `/api/v1/alerts/rules` | `page`, `page_size`, `enabled` | Paginated alert rules |
| POST | `/api/v1/alerts/rules` | `AlertRuleCreate` | Create keyword rule |
| GET | `/api/v1/alerts/rules/{rule_id}` | None | Get rule |
| PATCH | `/api/v1/alerts/rules/{rule_id}` | `AlertRuleUpdate` | Update rule |
| DELETE | `/api/v1/alerts/rules/{rule_id}` | None | Delete rule, returns 204 |
| GET | `/api/v1/alerts/events` | `page`, `page_size`, `rule_id` | Paginated alert events |
| POST | `/api/v1/alerts/evaluate/{article_id}` | None | Evaluate all enabled rules for an article |

## Briefings

| Method | Path | Query / Body | Notes |
| --- | --- | --- | --- |
| GET | `/api/v1/briefings/daily` | `hours` (1–168, default 24), `limit` (1–50, default 20), `min_relevance` (optional 0–10, default **6.0** via `BRIEFING_MIN_RELEVANCE`), `lang` (optional), `format` (`json` \| `markdown`) | Aggregated daily briefing from articles with intelligence reports, sorted by `relevance_score` desc |

Response `data` shape:

```json
{
  "meta": {
    "generated_at": "2026-05-20T08:00:00Z",
    "window_hours": 24,
    "window_start": "2026-05-19T08:00:00Z",
    "window_end": "2026-05-20T08:00:00Z",
    "item_count": 12,
    "limit": 20,
    "min_relevance": 6.0,
    "ai_mode": "live|mock",
    "sort": "relevance_score_desc"
  },
  "overview": "过去时间窗内共 12 条高相关情报…",
  "items": [
    {
      "rank": 1,
      "article_id": 42,
      "source_id": 3,
      "source_name": "CISA Alerts",
      "title": "...",
      "url": "https://...",
      "published_at": "2026-05-20T02:00:00Z",
      "summary": "...",
      "tags": ["cyber"],
      "relevance_score": 8.5,
      "sentiment": "neutral",
      "model": "mock"
    }
  ],
  "markdown": null
}
```

When `format=markdown`, `data.markdown` contains a rendered briefing document; JSON wrapper is unchanged.

`min_relevance` controls the minimum intelligence report `relevance_score` included in the briefing. If the query parameter is omitted, the backend uses `BRIEFING_MIN_RELEVANCE`; if that env var is unset, the default threshold is `6.0`. The response `meta.min_relevance` reflects the resolved threshold used for the request.

## Briefing Delivery (Worker / Env)

Daily briefing delivery is triggered automatically by the `generate-daily-briefing` Celery Beat task (UTC 06:00). No public API endpoint exposes push — delivery runs inside the worker process after briefing generation.

**Environment variables:**

| Variable | Default | Description |
| --- | --- | --- |
| `BRIEFING_MIN_RELEVANCE` | `6.0` | Default minimum `relevance_score` for daily briefing items when request `min_relevance` is omitted |
| `BRIEFING_PUSH_ENABLED` | `true` | Master switch for push delivery |
| `FEISHU_WEBHOOK_URL` | (empty) | Feishu bot webhook URL. Empty → skip |
| `BRIEFING_PUBLIC_BASE_URL` | `http://localhost:3000` | Base URL for "查看完整简报" button |
| `FEISHU_PUSH_TOP_N` | `5` | Number of top articles shown in Feishu card |

**Worker return shape** (Celery result):

```json
{
  "briefing": { "...DailyBriefingRead..." },
  "delivery": {
    "channel": "feishu",
    "status": "sent|failed|skipped",
    "detail": "feishu 200",
    "error_message": null,
    "duration_ms": 123,
    "webhook_status_code": 200,
    "log_id": 7
  }
}
```

Delivery logs are persisted in the `briefing_delivery_logs` table regardless of status.

## AI

| Method | Path | Notes |
| --- | --- | --- |
| POST | `/api/v1/ai/chat` | Generic chat endpoint |
| GET | `/api/v1/ai/prompts` | List prompt templates available to backend |

## Agent Runtime

| Method | Path | Notes |
| --- | --- | --- |
| POST | `/api/v1/agents/runs` | Start a 12-factor agent run |
| GET | `/api/v1/agents/runs` | List runs |
| GET | `/api/v1/agents/runs/{run_id}` | Get run state |
| POST | `/api/v1/agents/runs/{run_id}/resume` | Resume paused run |
| GET | `/api/v1/agents/tools` | List registered tools |

## Frontend Contract

Frontend API wrapper:

- `apps/web/src/lib/api.ts`
- `apps/web/src/lib/intel-api.ts`
- `apps/web/src/types/intel.ts`

When changing endpoints, update:

- Backend routers and schemas under `backend/app/**`.
- Frontend types under `apps/web/src/types/**`.
- This document.

## Open API Questions

- Authentication headers are待补充.
- Rate limiting behavior is待补充.
- Error normalization for validation errors is待补充.
- Pagination upper limits are待补充.
