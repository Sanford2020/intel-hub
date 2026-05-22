# TASKS.md

任务看板 — **Single Master Agent** 调度 **Skills**。老板模式见 `workflows/autonomous-delivery.md`。

**多迭代路线图：** `docs/plans/roadmap-3-employees.md`（Sprint S1→S4，含 S1.5 UI 插队派单依据）

## BACKLOG

### M7 候选（S3 完成后四选一）

- M7-A 双语简报（中文化海外信息）
- M7-B Setup Wizard（5 分钟跑起来）
- M7-C AI 成本守门（限额 / 队列优先级 / mock 透明）
- M7-D Postgres 全文检索

### 长期

- 多租户隔离与配额（M8+）
- Elasticsearch / 向量检索
- 实体关系图
- Mobile / 推送 App
- 翻译质量评估 + 人工反馈环

## TODO

### S1 · M5 Daily Archive & Trends（当前 Sprint · 已批准派单）

派单顺序见 `docs/plans/roadmap-3-employees.md` §2；详细规划见 `docs/plans/M5-daily-archive-trends.md`。

| Task | Skill | 状态 | 依赖 |
| --- | --- | --- | --- |
| TASK-20260521-M5-M: ADR + PRD scenario 10 + 看板维护 | Cursor · Master | TODO | — |
| TASK-20260521-M5-A: migration + metrics + Celery archive task | Windsurf · Backend | TODO | M5-M Accepted |
| TASK-20260521-M5-B: archives/trends API | Windsurf · Backend | TODO | M5-A |
| TASK-20260521-M5-C: `/archives` + `/trends` UI | Windsurf · Frontend | TODO | M5-B |
| TASK-20260521-M5-D: pytest + acceptance + Review 报告 | Codex | TODO | M5-A 起即可 |

### S1.5 · M5.5 Frontend Intelligence Workbench Redesign（UI 规划完成 · 可派单）

派单依据 `docs/plans/M5.5-frontend-intelligence-workbench-redesign.md`。
执行原则：F1 可立即启动；F2 中的 `/archives`、`/trends` 视觉合流需等 M5-C 稳定，避免文件冲突。

| Task | Skill | 状态 | 依赖 |
| --- | --- | --- | --- |
| TASK-20260522-UI-F1: navigation + design components + dashboard homepage | Windsurf · Frontend | TODO | — |
| TASK-20260522-UI-F2: briefing/articles/sources/alerts visual alignment | Windsurf · Frontend | TODO | UI-F1；archives/trends 依赖 M5-C |
| TASK-20260522-UI-QA: frontend lint/build/test + route smoke + Review evidence | Codex · Test/Review | TODO | UI-F1 起；完整 QA 依赖 UI-F2 |
| TASK-20260522-UI-R: Master Review + 看板收口 | Cursor · Review | TODO | UI-QA |

### S2 · M3.5 Ops Closure（与 S1 并行 · 文件不冲突）

派单依据 `docs/plans/roadmap-3-employees.md` §3。

| Task | Skill | 状态 |
| --- | --- | --- |
| TASK-20260521-OPS-01: RSS 源健康清单 v2 | Codex · Test | TODO |
| TASK-20260521-OPS-02: `validate_project.sh` + GitHub Actions CI | Codex · Deployment | TODO |
| TASK-20260521-OPS-03: Worker / Beat 24h 观测落档 | Codex · Test | TODO |
| TASK-20260521-OPS-04: 解决 `DECISIONS.md` vs `docs/decisions.md` 权威性 | Cursor · Documentation | TODO |

### S3 · M6 Commercial Auth Foundation（S1 DONE 后启动 · 强串行）

派单依据 `docs/plans/roadmap-3-employees.md` §4。

| Task | Skill | 状态 | 依赖 |
| --- | --- | --- | --- |
| TASK-20260601-M6-ADR: 鉴权 ADR + 子任务拆解 | Cursor · Architecture | TODO | S1 DONE |
| TASK-20260601-M6-A: User / Session / JWT scaffold | Windsurf · Backend | TODO | M6-ADR |
| TASK-20260601-M6-B: 受保护路由 + RBAC | Windsurf · Backend | TODO | M6-A |
| TASK-20260601-M6-C: `/login` + AuthProvider + 路由守卫 | Windsurf · Frontend | TODO | M6-B |
| TASK-20260601-M6-D: 鉴权测试 + 部署 + 文档 | Codex | TODO | M6-A 起即可 |

## DOING

- None

## REVIEW

- None

## DONE

### M4 Intel Stack Integration — 2026-05-19

见 `docs/integrations-m4.md`

| Task | Skill | 状态 |
| --- | --- | --- |
| TASK-20260519-M4-A: RSSHub docker + rsshub-x seeds + OSINT RSS | Backend | DONE |
| TASK-20260519-M4-B: `aihot` / `apify` parsers + pipeline | Backend | DONE |
| TASK-20260519-M4-C: n8n / Telegram 简报出站 + config 补全 | Backend | DONE |
| TASK-20260519-M4-D: 前端类型、batch 脚本、pytest | Frontend + Codex | DONE |

摘要：`docs/integrations-m4.md`、RSSHub docker、`aihot`/`apify` 连接器、n8n/Telegram 出站；
seeds 含 osint-rss / aihot-api / rsshub-x（25 条）+ BestBlogs 策展（7 条）+ `ingest-social-fast` 优先队列；**71 pytest passing**。

### M4.7 Trend Aggregators — 2026-05-22

见 `docs/plans/M4.7-trend-aggregator-sources.md`

- `trends_parser.py` + pipeline `trends` 类型
- 4 源：trends24 / getdaytrends / trend-calendar (X + Google)
- `test_trends_parser.py` + `ingest-social-fast` 优先 slug

### M2 Operator Closure — 2026-05-21

- **TASK-20260521-01:** `run-daily-intel.ps1`, `docs/OWNER.md`, PRD 8–9, `autonomous-delivery.md`
- **TASK-20260521-02:** `docs/deployment.md` Daily Operations

- TASK-20260520-03 飞书推送
- TASK-20260520-02 相关度 + 今日精选
- TASK-20260520-01 每日简报
- TASK-20260519-01 validate_project.ps1

### Earlier

- AI Dev OS Bootstrap v2/v1、Sprint 6 operational loop

## BLOCKED

- None
