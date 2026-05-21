# Architecture Details（Intel Hub）

> 摘要见根目录 `ARCHITECTURE.md`。本文档补充模块与实现细节。不确定处标 **TODO/UNKNOWN**。

## 1. Backend 分层

```text
backend/app/main.py          FastAPI 入口
backend/app/api/router.py    聚合 /api/v1 路由
backend/app/modules/         领域模块（sources, articles, ingest, intelligence, alerts）
backend/app/models/          SQLAlchemy ORM
backend/app/db/              异步/同步 Session、Alembic
backend/app/api/v1/endpoints/  health, stats, ai, agents
```

## 2. 领域模块

| 模块 | 路径 | 说明 |
| --- | --- | --- |
| Sources | `modules/sources/` | CRUD、import、ingest 触发、ingest-logs |
| Articles | `modules/articles/` | CRUD、过滤、analyze 触发 |
| Ingest | `modules/ingest/` | RSS 解析、`ingest_rss_source` 管道 |
| Intelligence | `modules/intelligence/` | AI/mock 分析 |
| Alerts | `modules/alerts/` | 规则、匹配、事件、notifier stub |

## 3. Worker 任务

```text
workers/celery_app.py                    Beat 调度
workers/tasks/ingest/fetch_rss.py        RSS 采集
workers/tasks/analyze/summarize.py       文章分析
workers/tasks/analyze/dispatch.py        未分析文章调度
workers/tasks/alerts/match.py            告警评估
```

**注意**：任务模块须在 `workers/tasks/*/__init__.py` 中 import，Celery 才能 autodiscover。

## 4. 前端结构

```text
apps/web/src/app/           Next.js App Router 页面
apps/web/src/lib/intel-api.ts   API 封装
apps/web/src/types/intel.ts     类型定义
```

页面：`/`、`/sources`、`/articles`、`/articles/[id]`、`/alerts`（以实际目录为准）。

## 5. 数据模型（概念）

```text
Source → IngestLog
Source → Article → IntelligenceReport
AlertRule → AlertEvent ← Article
```

去重：`Article.content_hash`。

## 6. 外部集成

| 依赖 | 用途 |
| --- | --- |
| PostgreSQL | 主存储 |
| Redis | Celery broker/backend |
| OpenAI API | 可选；无 key 则 mock |
| RSS/HTTP | 采集源 URL |

## 7. 脚本与种子

| 脚本 | 用途 |
| --- | --- |
| `scripts/seed-sources.py` | API 导入来源 |
| `scripts/batch-ingest-rss.py` | 批量采集（`--async`） |
| `scripts/parse-data-sources.py` | 从 docs markdown 生成 seeds |
| `scripts/backfill-source-urls.py` | 补空 URL |

## 8. 测试布局

- `backend/tests/` — pytest（约 31 项，本地已验证过）
- `apps/web/__tests__/` — 前端单测（**覆盖范围 TODO**）
- E2E 浏览器测试 — **UNKNOWN / 未 formalize**

## 9. 配置

- `backend/.env` — DB、Redis、OpenAI、Celery
- `apps/web/.env.local` — `NEXT_PUBLIC_API_URL`
- 根 `.env` — Docker Compose

## 10. 已知实现细节（观察记录，非代码修改）

- Windows Celery 建议 `--pool solo`（`scripts/dev.ps1`）
- `POST .../ingest?async=1` 非阻塞入队
- 同步 batch ingest 可长时间占用 API 进程

## 11. 待确认（TODO）

- Commercial Auth 模块位置：**UNKNOWN**
- 生产 hosting：**TODO**
- 全文检索方案：**TODO**（v0.2+）
- `docs/decisions.md` 与根 `DECISIONS.md` 权威关系：**TODO**
