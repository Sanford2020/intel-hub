# Intel Hub — 架构规划

## 系统图

```
                    ┌─────────────────────────────────────┐
                    │           apps/web (Dashboard)       │
                    └──────────────────┬──────────────────┘
                                       │ REST
                    ┌──────────────────▼──────────────────┐
                    │         backend (FastAPI)            │
                    │  /sources /articles /search /alerts  │
                    └──────┬───────────────────┬──────────┘
                           │                   │
              ┌────────────▼────────┐   ┌──────▼──────┐
              │  PostgreSQL        │   │   Redis     │
              │  sources, articles │   │   queue     │
              │  intel_reports     │   └──────┬──────┘
              └────────────────────┘          │
                                    ┌─────────▼─────────┐
                                    │  Celery Workers    │
                                    │  ingest · analyze  │
                                    └─────────┬─────────┘
                                              │
                                    ┌─────────▼─────────┐
                                    │  External Sources  │
                                    │  RSS · API · Web   │
                                    └───────────────────┘
```

## 核心实体（规划）

| 实体 | 字段要点 |
|------|----------|
| Source | name, type(rss/api), url, schedule, enabled, tags |
| Article | source_id, title, url, content, published_at, hash(dedup) |
| IntelligenceReport | article_id, summary, tags[], entities[], sentiment, raw_json |
| AlertRule | keywords[], channels[], user_id |

## AI 流水线

```
Article raw → prompts/intelligence/analyze.yaml → structured JSON
{
  "summary": "...",
  "tags": ["geopolitics", "tech"],
  "entities": [{"name": "...", "type": "org"}],
  "relevance_score": 0.85
}
```

## 目录规划

```
backend/app/modules/
  sources/
  articles/
  intelligence/
  alerts/

workers/tasks/
  ingest/fetch_rss.py
  analyze/summarize.py

prompts/intelligence/
  analyze.yaml
  classify.yaml
```
