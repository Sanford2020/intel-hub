# M5 — 每日归档与趋势分析

> **Master:** Cursor · **开发:** Windsurf · **Review:** Codex  
> 状态：**已批准 · ADR-20260521-01 Accepted** · 2026-05-22

## 1. 背景与问题

当前 Intel Hub：

- **每日简报**（`/briefing`）是 **实时聚合**：从 `articles` + `intelligence_reports` 按时间窗查询，**不落库**。
- `generate_daily_briefing` Celery 任务（Beat 06:00 UTC）只推送飞书/n8n，**不保留历史快照**。
- 文章/报告持续累积（4000+），但 **无法回答**：
  - 「上周二 Top 10 是什么？」
  - 「过去 30 天 AI 类标签文章是否在增多？」
  - 「BestBlogs 源贡献占比趋势如何？」

**目标：** 在现有 Delivery Layer 之上增加 **Archive Layer** — 每日冻结快照 + 结构化指标，供趋势 API 与 UI 使用。

## 2. 产品定义

### 用户故事

| 角色 | 需求 |
|------|------|
| 老板 | 每天自动归档，不用手动导出 |
| 分析师 | 查看任意历史日的 Top 简报与当日统计 |
| 分析师 | 30/90 天趋势：入库量、高相关文章数、标签/分类分布 |

### 非目标（M5 不做）

- 冷存储到 S3 /  Parquet（M5.1+）
- 实体关系图、全文检索（已有 BACKLOG）
- 多租户归档隔离（Commercial Auth 之后）

## 3. 方案对比

| 方案 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| **A. 仅简报 JSON** | 每天存 `DailyBriefingRead` | 实现快 | 趋势需扫 articles，慢 |
| **B. 仅指标 rollup** | 每天存聚合数字 | 趋势查询快 | 无法回看历史 Top 条目 |
| **C. 混合（推荐）** | 简报快照 + `metrics_json` | 可读 + 可分析 | 单行略大（可控） |

**推荐 C**：一条 `daily_archives` 记录 = 当日可读简报 + 可图表化指标。

## 4. 数据模型

### 4.1 表 `daily_archives`

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | PK | |
| `archive_date` | `DATE` | 归档日历日，**UNIQUE** |
| `timezone` | `VARCHAR(64)` | 默认 `Asia/Shanghai` |
| `window_start` / `window_end` | `TIMESTAMPTZ` | 统计窗口（默认前 24h） |
| `briefing_json` | `JSONB` | 完整 `DailyBriefingRead`（含 items/markdown） |
| `metrics_json` | `JSONB` | 结构化指标（见 4.2） |
| `status` | `VARCHAR(16)` | `success` / `failed` / `partial` |
| `error_message` | `TEXT` | 可选 |
| `created_at` | `TIMESTAMPTZ` | |

索引：`(archive_date DESC)`，`metrics_json` 暂不 GIN（M5 数据量小）。

### 4.2 `metrics_json` Schema（v1）

```json
{
  "version": 1,
  "ingest": {
    "articles_created": 142,
    "by_source_type": { "rss": 80, "x": 10, "reddit": 52 },
    "by_category": { "wire": 30, "social": 40, "geopolitical": 25 }
  },
  "analysis": {
    "reports_created": 98,
    "avg_relevance": 5.4,
    "median_relevance": 5.0,
    "high_relevance_count": 18,
    "by_sentiment": { "neutral": 60, "negative": 20, "positive": 18 }
  },
  "tags_top": [{ "tag": "ai", "count": 24 }, { "tag": "ukraine", "count": 12 }],
  "entities_top": [{ "name": "OpenAI", "count": 8 }],
  "sources_top": [{ "slug": "bestblogs-ai-highscore-en", "count": 15 }],
  "alerts": { "events_created": 3 },
  "briefing_meta": {
    "item_count": 12,
    "min_relevance": 6.0,
    "ai_mode": "live"
  }
}
```

指标在归档任务内 **单次 SQL 聚合** 生成，避免事后扫全表。

## 5. 架构与数据流

```text
Beat 06:00  generate_daily_briefing  (已有)
     │
     ▼
Beat 06:15  archive_daily_snapshot   (新增，或在 briefing 任务末尾链式调用)
     │
     ├─ build_daily_briefing_sync(window=24h)
     ├─ compute_daily_metrics_sync(window)
     ├─ UPSERT daily_archives WHERE archive_date = today(tz)
     └─ (optional) 触发 delivery 若 briefing 未推

API:
  GET /api/v1/archives              → 日期列表 + 摘要指标
  GET /api/v1/archives/{date}       → 完整 briefing + metrics
  GET /api/v1/archives/trends       → 时间序列（见 6）

UI:
  /archives      历史日列表 + 点进详情
  /trends        折线/柱状（30/90 天）
```

**时区：** `ARCHIVE_TIMEZONE=Asia/Shanghai`，`archive_date` 按该时区的日历日划分。

**幂等：** 同一天重复跑 → `UPSERT` 覆盖（支持手动重跑 `scripts/backfill-archives.py`）。

## 6. API 设计

### `GET /api/v1/archives`

Query: `from`, `to`（ISO date），`page`, `page_size`

Response 摘要行：`archive_date`, `item_count`, `articles_created`, `high_relevance_count`, `status`

### `GET /api/v1/archives/{date}`

Response：`briefing` + `metrics` + `meta`

### `GET /api/v1/archives/trends`

Query:

| 参数 | 说明 |
|------|------|
| `days` | 7 / 30 / 90，默认 30 |
| `metric` | 见下表 |
| `tag` | 当 `metric=tag_count` 时必填 |

| metric | 含义 |
|--------|------|
| `articles_created` | 日入库量 |
| `reports_created` | 日分析量 |
| `high_relevance_count` | 相关度 ≥ 阈值文章数 |
| `avg_relevance` | 日均相关度 |
| `alert_events` | 告警事件数 |
| `tag_count` | 指定标签出现次数 |
| `category_count` | Query `category=wire` |

Response：`{ "metric": "...", "points": [{ "date": "2026-05-20", "value": 142 }] }`

## 7. 模块边界

```
backend/app/modules/archives/
  ├── models.py          # DailyArchive ORM（或 app/models/daily_archive.py）
  ├── metrics.py         # compute_daily_metrics_sync
  ├── service.py         # create_or_update_archive, list, get, trends
  ├── router.py          # API routes
  └── schemas.py

workers/tasks/archives/
  └── snapshot.py        # archive_daily_snapshot Celery task

apps/web/src/app/
  ├── archives/page.tsx
  └── trends/page.tsx
```

不修改 `articles` / `intelligence_reports` 表结构；归档 **只读** 现有数据。

## 8. 实施阶段与 Skill 分工

### Phase A — 数据层（Windsurf · Backend）

| ID | 任务 | 产出 |
|----|------|------|
| M5-A1 | Alembic migration `daily_archives` | 表 + 索引 |
| M5-A2 | `metrics.py` 聚合 SQL | 单元测试（sqlite） |
| M5-A3 | `ArchiveService.create_daily_archive()` | UPSERT 逻辑 |
| M5-A4 | Celery `archive_daily_snapshot` + Beat 06:15 | `celery_app.py` |
| M5-A5 | `scripts/backfill-archives.py --days N` | 历史补档 |

**验收：** 手动跑 task → DB 有今日一行；重复跑幂等。

### Phase B — API（Windsurf · Backend）

| ID | 任务 | 产出 |
|----|------|------|
| M5-B1 | `GET /archives` 列表 | 分页 |
| M5-B2 | `GET /archives/{date}` 详情 | |
| M5-B3 | `GET /archives/trends` | 7 种 metric |
| M5-B4 | 更新 `docs/api.md` | |

**验收：** curl 30 天 trends 返回 JSON 序列。

### Phase C — 前端（Windsurf · Frontend）

| ID | 任务 | 产出 |
|----|------|------|
| M5-C1 | `intel-api.ts` archives/trends 封装 | |
| M5-C2 | `/archives` 列表 + 详情抽屉 | 复用 briefing 卡片样式 |
| M5-C3 | `/trends` 简易图表 | CSS/SVG 或轻量 chart（不引入重型库优先） |
| M5-C4 | 导航入口（首页 / sidebar） | |

**验收：** 浏览器可看 30 天入库折线 + 点击某日历史简报。

### Phase D — Review & Ops（Codex）

| ID | 任务 | 产出 |
|----|------|------|
| M5-D1 | `test_archives.py` service + API + metrics | pytest |
| M5-D2 | 扩展 `acceptance-smoke.py` 检查 archives | |
| M5-D3 | `run-daily-intel.ps1` 末尾可选 `--archive` | |
| M5-D4 | `docs/deployment.md` Beat 说明 | |
| M5-D5 | **Review 报告**：性能、JSON 大小、时区、幂等 | `REVIEW.md` 条目 |

**验收：** pytest 全绿；Review 无 BLOCK。

### Cursor（Master）职责

- 本文档 + ADR 写入 `DECISIONS.md`
- `TASKS.md` 看板维护
- Windsurf 交付后 **功能/架构 Review**
- 不要求 Master 写实现代码

## 9. 配置项

| 环境变量 | 默认 | 说明 |
|----------|------|------|
| `ARCHIVE_ENABLED` | `true` | 总开关 |
| `ARCHIVE_TIMEZONE` | `Asia/Shanghai` | **北京时间**归档日历日 |
| `ARCHIVE_WINDOW_HOURS` | `24` | 与简报一致 |
| `ARCHIVE_BRIEFING_LIMIT` | `20` | 快照 Top N |
| `ARCHIVE_MIN_RELEVANCE` | 同 `BRIEFING_MIN_RELEVANCE` | 高相关阈值 |

### 业务分类热度（核心趋势维度）

按 `sources.category`（见 `00-intelligence-taxonomy.md`）聚合，每日写入 `metrics_json.category_heat`：

```json
{
  "category": "geopolitical",
  "category_label": "地缘/OSINT",
  "articles": 45,
  "reports": 38,
  "high_relevance": 12,
  "avg_relevance": 5.8,
  "heat_score": 81.0
}
```

**热度公式（v1，可解释）：**

```text
heat_score = articles + 3 × high_relevance + avg_relevance
```

（`high_relevance` = 该分类下 `relevance_score ≥ ARCHIVE_MIN_RELEVANCE` 的报告数）

**趋势 API 主入口：**

`GET /api/v1/archives/trends/category-heat?days=30`

返回各分类 30 天 `heat_score` 序列，供 `/trends` 折线/热力对比。

## 10. 风险与缓解

| 风险 | 缓解 |
|------|------|
| `briefing_json` 过大 | Top 20 + 截断 overview；M5.1 可拆表 |
| 首日无数据 trends 空 | backfill 脚本 + UI 空状态 |
| Beat 与 briefing 竞态 | archive 排 06:15，或在 briefing task 内 `chain` |
| 4000+ 文章聚合慢 | 指标 SQL 带 `window_start` 索引过滤 |

## 11. 成功标准（老板验收）

1. Beat 跑一天后，`daily_archives` 自动多一行。
2. `/archives` 可打开昨日简报，内容与当日 `/briefing` 一致。
3. `/trends?days=30&metric=articles_created` 返回 ≥1 数据点（backfill 后 ≥7）。
4. pytest + acceptance 通过，Codex Review 无 BLOCK。

## 12. 后续（M5.1+）

- 周/月归档 rollup（`weekly_archives`）
- 导出 CSV / Notion 同步
- 标签共现矩阵、实体趋势
- 归档 JSON 导出到对象存储

---

**批准后开始：** Windsurf 执行 Phase A → B → C；Codex Phase D。
