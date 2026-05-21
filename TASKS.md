# TASKS.md

任务看板 — **Single Master Agent** 调度 **Skills**。老板模式见 `workflows/autonomous-delivery.md`。

## BACKLOG

- Commercial authentication and authorization model
- Production deployment hardening
- Worker/beat 24h observation + `docs/operations/` record
- Full-text search (v0.2+)
- Entity relationship graph
- **Stickiness Phase 2:** Setup wizard、简报英中双语
- Commercial auth scope ADR（Architecture）
- `OPENAI_API_KEY` production strategy（Deployment）
- Curate broken RSS feeds → `REVIEW.md`（Backend）
- Resolve `DECISIONS.md` vs `docs/decisions.md` authority

## TODO

### M5 Daily Archive & Trends（Master 规划完成 → 待批准开发）

见 `docs/plans/M5-daily-archive-trends.md`

| Task | Skill | 状态 |
| --- | --- | --- |
| TASK-20260521-M5-A: migration + metrics + Celery archive task | Windsurf · Backend | TODO |
| TASK-20260521-M5-B: archives/trends API | Windsurf · Backend | TODO |
| TASK-20260521-M5-C: `/archives` + `/trends` UI | Windsurf · Frontend | TODO |
| TASK-20260521-M5-D: pytest + acceptance + Review 报告 | Codex | TODO |
| TASK-20260521-M5-M: ADR + PRD 更新 | Cursor · Master | TODO |

### M3 Ops Hardening

- TASK-20260521-03: RSS 源健康清单 + `REVIEW.md` 更新（Codex + Backend）
- TASK-20260521-04: `validate_project.ps1` 全量（含 build + docker config）纳入 CI 说明

### M4 Intel Stack Integration（Master 当前 Sprint）

见 `docs/integrations-m4.md`

| Task | Skill | 状态 |
| --- | --- | --- |
| TASK-20260519-M4-A: RSSHub docker + rsshub-x seeds + OSINT RSS | Backend | DONE |
| TASK-20260519-M4-B: `aihot` / `apify` parsers + pipeline | Backend | DONE |
| TASK-20260519-M4-C: n8n / Telegram 简报出站 + config 补全 | Backend | DONE |
| TASK-20260519-M4-D: 前端类型、batch 脚本、pytest | Frontend + Codex | DONE |

## DOING

- None

## REVIEW

- None

## DONE

### M4 Intel Stack Integration — 2026-05-19

- `docs/integrations-m4.md`、RSSHub docker、`aihot`/`apify` 连接器、n8n/Telegram 出站
- Seeds: `osint-rss-sources.json`、`aihot-api-sources.json`、`rsshub-x-sources.json`（25 条）
- **BestBlogs 策展 RSS**：`bestblogs-sources.json`（7 条）+ `ingest-social-fast` 优先队列
- **71 pytest passing**

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
