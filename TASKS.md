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



### S1.5 · M5.5 Frontend Intelligence Workbench Redesign



派单依据 `docs/plans/M5.5-frontend-intelligence-workbench-redesign.md`。

**Master UI-R (2026-05-22):** Codex UI-QA **REQUEST_CHANGES** — F2 主目标已达成，P1 移动 overflow + P2 trends key 待修后再签收。



| Task | Skill | 状态 | 依赖 |

| --- | --- | --- | --- |

| TASK-20260522-UI-F2-FIX: 390px overflow + trends duplicate keys | Cursor · Frontend | DONE | 390px recheck PASS |
| TASK-20260522-UI-QA-RECHECK: lint/build/smoke 复测 | Codex · Test/Review | DONE | lint/type-check/build PASS; 390px browser PASS |

| TASK-20260522-UI-R: Master Review + 看板收口 | Cursor · Review | **APPROVE** | F2-FIX recheck 2026-05-23 |



### S2 · M3.5 Ops Closure（与 S1 并行 · 文件不冲突）



派单依据 `docs/plans/roadmap-3-employees.md` §3。



| Task | Skill | 状态 |

| --- | --- | --- |
| TASK-20260521-OPS-03: Worker / Beat 24h 观测落档 | Cursor · Test | **APPROVE with risk** | Extended ~39m run + tooling; 24h runbook `ops-worker-observe.ps1` |



### S3 · M6 Commercial Auth Foundation（S1 DONE · ADR Accepted · 强串行）



派单依据 `docs/plans/M6-commercial-auth-foundation.md` · **ADR-20260601-01 Accepted**。



| Task | Skill | 状态 | 依赖 | Files / 交付 |

| --- | --- | --- | --- | --- |

| TASK-20260601-M6-A: User / Session / JWT scaffold | Cursor · Backend | DONE | pytest 91 passed |
| TASK-20260601-M6-B: 受保护路由 + RBAC | Cursor · Backend | DONE | router 级保护 + write RBAC |
| TASK-20260601-M6-C: `/login` + AuthProvider + 路由守卫 | Cursor · Frontend | DONE | middleware 排除 `/api/*` |
| TASK-20260601-M6-D: 鉴权测试 + 部署 + 文档 | Cursor | DONE | live smoke ALL PASS @ :8001 |



## DOING



- None



## REVIEW

### S1.5 · M5.5 UI — Codex REQUEST_CHANGES · Master UI-R 同步

| Task | Skill | 状态 | Notes |
| --- | --- | --- | --- |
| TASK-20260522-UI-F2: intelligence pages visual alignment | Windsurf · Frontend | REVIEW | briefing/trends/archives 已合流共享 shell；QA 未 APPROVE |
| TASK-20260522-UI-QA: F2 recheck | Codex · Test | REVIEW | Verdict **REQUEST_CHANGES** — 见 `docs/operations/frontend-ui-qa-2026-05.md` |
| TASK-20260522-UI-R: Master Review | Cursor · Review | REVIEW | Verdict **REQUEST_CHANGES**（与 Codex 一致）；不虚假 DONE |

## DONE



### S1.5 · M5.5 UI Workbench — F1 — 2026-05-22

| Task | Skill | 结果 |
| --- | --- | --- |
| TASK-20260522-UI-F1: navigation + design components + dashboard homepage | Windsurf · Frontend | 分组导航、移动菜单、暗色、共享 UI 组件、今日情报工作台 |

### S1 · M5 Daily Archive & Trends — 2026-05-22 ✅



| Task | Skill | 结果 |

| --- | --- | --- |

| TASK-20260521-M5-A: migration + metrics + Celery archive task | Windsurf · Backend | `006_daily_archives` + Beat + backfill |

| TASK-20260521-M5-B: archives/trends API | Windsurf · Backend | `/archives`, `/trends/category-heat` |

| TASK-20260521-M5-C: `/archives` + `/trends` UI | Windsurf · Frontend | 路由 + API 联调 |

| TASK-20260521-M5-D: pytest + acceptance + Review | Codex | root pytest 80 passed；live smoke **ALL PASS** @ `:8001` |



### S1 · M5 Master + S2 · OPS-04 — 2026-05-22



| Task | Skill | 结果 |

| --- | --- | --- |

| TASK-20260521-M5-M: ADR + PRD scenario 10 + 看板维护 | Cursor · Master | ADR-20260521-01 Accepted；PRD §10；TASKS 同步 |

| TASK-20260521-OPS-04: `DECISIONS.md` vs `docs/decisions.md` 权威性 | Cursor · Documentation | ADR-20260521-03 Accepted；redirect + archive |



### S3 · M6 Commercial Auth — ADR — 2026-06-01

| Task | Skill | 结果 |
| --- | --- | --- |
| TASK-20260601-M6-ADR: 鉴权 ADR + 子任务拆解 | Cursor · Architecture | ADR-20260601-01 Accepted；`docs/plans/M6-commercial-auth-foundation.md`；task-cards M6-A/B/C/D |

### M4 Intel Stack Integration — 2026-05-19



见 `docs/integrations-m4.md`



| Task | Skill | 状态 |

| --- | --- | --- |

| TASK-20260519-M4-A: RSSHub docker + rsshub-x seeds + OSINT RSS | Backend | DONE |

| TASK-20260519-M4-B: `aihot` / `apify` parsers + pipeline | Backend | DONE |

| TASK-20260519-M4-C: n8n / Telegram 简报出站 + config 补全 | Backend | DONE |

| TASK-20260519-M4-D: 前端类型、batch 脚本、pytest | Frontend + Codex | DONE |



摘要：`docs/integrations-m4.md`、RSSHub docker、`aihot`/`apify` 连接器、n8n/Telegram 出站；

seeds 含 osint-rss / aihot-api / rsshub-x（25 条）+ BestBlogs 策展（7 条）+ `ingest-social-fast` 优先队列；**76 pytest passing**（含 archives）。



### M4.7 Trend Aggregators — 2026-05-22

见 `docs/plans/M4.7-trend-aggregator-sources.md`

- `trends_parser.py` + pipeline `trends` 类型
- 4 源：trends24 / getdaytrends / trend-calendar (X + Google)
- `test_trends_parser.py` + `ingest-social-fast` 优先 slug

### M2 Operator Closure — 2026-05-21



- **TASK-20260521-01:** `run-daily-intel.ps1`, `docs/OWNER.md`, PRD 8–9, `autonomous-delivery.md`

- **TASK-20260521-02:** `docs/deployment.md` Daily Operations

### S2 · Ops — 2026-05-22

| Task | Skill | 结果 |
| --- | --- | --- |
| TASK-20260521-OPS-01: RSS 源健康清单 v2 | Codex · Test | `probe-rss-health.py` + `docs/operations/rss-health-2026-05.md`；坏源 seeds disabled |
| TASK-20260521-OPS-02: validate + CI | Codex · Deployment | `validate_project.sh` + `.github/workflows/ci.yml` + `make ci` |

- TASK-20260520-03 飞书推送

- TASK-20260520-02 相关度 + 今日精选

- TASK-20260520-01 每日简报

- TASK-20260519-01 validate_project.ps1



### Earlier



- AI Dev OS Bootstrap v2/v1、Sprint 6 operational loop

- **Roadmap PR #1:** `docs/plans/roadmap-3-employees.md` + task-cards M5/OPS

- **M5.5 plan PR #3:** `docs/plans/M5.5-frontend-intelligence-workbench-redesign.md` + UI task-cards



## BLOCKED

- None

