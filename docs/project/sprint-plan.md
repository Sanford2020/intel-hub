# Intel Hub — Sprint 计划



> Commercial Edition baseline 已交付。当前重点是商业可运营：系统稳定、验证可复现、采集/分析/告警链路可长期运行。



## Sprint 0 — 项目初始化 ✅



## Sprint 1 — 数据基础 ✅



## Sprint 2 — 采集 Worker ✅



## Sprint 3 — AI intelligence ✅



## Sprint 4 — 检索与 Dashboard ✅



## Sprint 5 — 告警 ✅



- [x] `AlertRule` + `AlertEvent` 模型 + Alembic `004_alerts`

- [x] CRUD `/api/v1/alerts/rules` + `/events` + `/evaluate/{article_id}`

- [x] 关键词匹配（title / content / tags / summary）

- [x] 通知 stub：`log` · `webhook` · `email_stub`

- [x] 分析完成后自动评估告警

- [x] Celery `workers/tasks/alerts/match.py`

- [x] 前端 `/alerts` + 首页统计 `GET /stats/overview`



## Commercial Edition Baseline — 已交付 ✅



对照 [intel-hub-brief.md](./intel-hub-brief.md) 商业版基础能力全部完成。



## Sprint 6 — 运营闭环 🔄

- [x] Worker + Beat 常驻（Windows 使用 `--pool solo`）
- [x] 修复 Celery 未注册 analyze/alerts 任务
- [x] 批量 RSS 采集 `scripts/batch-ingest-rss.py`（支持 `--async` 非阻塞）
- [x] `--replace` 重导 506 来源 URL（来自 markdown）
- [x] `POST /sources/{id}/ingest?async=1` 异步采集 API
- [ ] 配置 `OPENAI_API_KEY` 启用真实 AI（当前 mock）
- [ ] 24h 自动运行观察

## 当前状态

**Sprint 6 进行中** — 采集→分析→告警闭环已首次跑通；Beat 每 5/10 分钟自动调度。

## 商业增强项

- [ ] 多租户 / 权限

- [ ] 全文检索（Elasticsearch / pg_trgm）

- [ ] 自动翻译流水线

- [ ] 实体关系图谱

- [ ] 移动端 / 推送

