# DECISIONS.md

Architecture Decision Records for Intel Hub. Add a new entry whenever the project changes architecture, API contracts, data model, infrastructure, agent workflow, or commercial delivery assumptions.

## ADR Template

```markdown
## ADR-YYYYMMDD-NN: Title

Date: YYYY-MM-DD
Status: Proposed | Accepted | Rejected | Superseded
Owner: Master | Skill name | Human

### Context

What problem, constraint, or opportunity led to this decision?

### Decision

What did we decide?

### Alternatives

1. Option A
2. Option B

### Tradeoffs

- Pros:
- Cons:

### Risks

- ...

### Follow-up

- [ ] Task or doc update
- [ ] Test or migration
- [ ] Review checkpoint
```

## ADR-20260519-01: Use Cursor + Windsurf + Codex Operating Model

Date: 2026-05-19
Status: Accepted
Owner: Human

### Background

The project needs a repeatable AI development operating system so multiple AI tools can cooperate without overwriting each other or drifting from product goals.

### Decision

Use Cursor as the planning and architecture coordinator, Windsurf as the focused feature implementation agent, Codex as the execution/testing/debugging agent, and a Review Agent as the quality gate.

### Alternatives Considered

1. Use one AI agent for every task.
2. Keep ad hoc chat-only coordination.
3. Use separate agent-specific docs without a shared task board.

### Impact

- Positive: Clear ownership, safer handoffs, better review checkpoints.
- Negative: More process files to maintain.
- Operational: `TASKS.md`, `AGENTS.md`, `REVIEW.md`, and `workflows/` become coordination sources.
- Security: Review gate makes risky changes more visible.
- Cost: Slightly more planning overhead per task.

### Follow-up Actions

- [ ] Keep task board current after each agent handoff.
- [ ] Add missing commercial readiness tasks.

## ADR-20260519-02: AI Development Operating System File Layout

Date: 2026-05-19
Status: Accepted
Owner: Human

### Background

Multiple AI tools (Cursor, Windsurf, Codex) need shared task, architecture, review, and prompt files without modifying business code during initialization.

### Decision

Standardize on root-level `AGENTS.md`, `TASKS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `REVIEW.md`, plus `docs/prd.md`, `docs/api.md`, `docs/deployment.md`, `prompts/*-agent.md`, and `workflows/*.md`.

### Alternatives Considered

1. Keep coordination only in chat history.
2. Store everything under `.cursor/` only.
3. Duplicate docs per tool without a task board.

### Impact

- Positive: Repeatable handoffs and review gates.
- Negative: Documentation surface area increases.
- Operational: Agents must update `TASKS.md` on status changes.
- Security: Review workflow makes risky changes visible before merge.

### Follow-up Actions

- [ ] Run first full cycle: Cursor plan → Windsurf → Codex → Review.
- [ ] Resolve duplicate ADR locations (`DECISIONS.md` vs `docs/decisions.md`).

## ADR-20260519-03: Single Master Agent + Multiple Skills

Date: 2026-05-19
Status: Accepted
Owner: Human

### Context

Multiple AI tools without a single coordinator caused overlapping edits and context pollution.

### Decision

Adopt Single Master Agent (Cursor) + Skills (`SKILLS.md`, `prompts/skill-*.md`). Windsurf/Codex execute Skills; they are not independent architects.

### Alternatives

1. Multi autonomous agents with equal authority.
2. Chat-only coordination without TASK board.
3. Tool-specific docs only (no shared SKILLS.md).

### Tradeoffs

- Pros: Clear ownership, less chaos, reusable Skill prompts for Claude/GPT.
- Cons: Master must maintain TASKS/docs overhead.

### Risks

- Skill boundaries ignored without Review gate.
- Legacy prompt files may confuse until Master maps them.

### Follow-up

- [ ] Run one full standard-development cycle on next TODO.
- [ ] Add `docs/operations/` for release/observation logs.

## ADR-20260520-01: Add Delivery Layer (Horizon-Inspired, Platform-Preserving)

Date: 2026-05-20
Status: Accepted
Owner: Master (Human confirmed)

### Context

Intel Hub has strong ingest/storage/API but weak user stickiness vs tools like Horizon. Users need a daily readable artifact and push, not only CRUD lists.

### Decision

Add a **Delivery Layer** on top of existing platform: daily briefing + relevance scoring + Feishu push. Keep PostgreSQL, sources taxonomy, Celery, and admin UI as the system of record. Do not pivot to personal JSON-config-only tool.

### Alternatives

1. Fork/replace with Horizon for reading; keep Intel Hub as backend only.
2. Build full Horizon parity (HN/Reddit/comments/bilingual site).
3. Status quo — dashboard only.

### Tradeoffs

- Pros: Stickiness without abandoning intel-platform identity; reuses articles/reports/alerts.
- Cons: New module surface; AI scoring quality depends on provider/mock labeling.

### Risks

- Scope creep into Horizon clone; mitigate via explicit Out-of-Scope per TASK.
- Push webhook abuse if exposed publicly before Auth.

### Follow-up

- [x] Execute TASK-20260520-01 → 02 → 03.
- [ ] Update `docs/prd.md` core scenarios 8–9 (daily briefing, push).

## ADR-20260521-01: Daily Archive Layer for Historical Briefings and Trends

Date: 2026-05-21
Status: Proposed
Owner: Cursor (Master)

### Context

Daily briefing is computed on-the-fly; no day-boundary snapshots exist. Operators cannot compare metrics or re-read past Top-N digests as the corpus grows (4000+ articles).

### Decision

Add **Archive Layer**: table `daily_archives` with per-calendar-day `briefing_json` + `metrics_json`. Celery task `archive_daily_snapshot` runs after daily briefing (Beat 06:15 UTC). Expose `GET /archives`, `/archives/{date}`, `/archives/trends` and UI `/archives`, `/trends`.

### Alternatives

1. Briefing JSON only — no structured trends.
2. Metrics only — no historical readable digest.
3. Export articles to cold storage — heavier, deferred to M5.1.

### Tradeoffs

- Pros: Fast trend queries; preserves readable history; minimal change to existing tables.
- Cons: JSON row growth; timezone semantics must be documented.

### Risks

- Beat ordering vs briefing task — mitigate with 15min offset or task chain.
- Large `briefing_json` — cap at Top 20 items.

### Follow-up

- [ ] Approve `docs/plans/M5-daily-archive-trends.md`
- [ ] Windsurf Phase A–C; Codex Phase D
- [ ] Update PRD scenario 10 (archives/trends)

## ADR-20260521-02: Three-Employee Delivery Cadence (Cursor / Windsurf / Codex)

Date: 2026-05-21
Status: Proposed
Owner: Cursor (Master)

### Context

老板希望让 3 个 AI 员工（Cursor / Codex / Windsurf）持续完善 Intel Hub。原有 `AGENTS.md` 与 `SKILLS.md` 已经规定 Single Master + Multiple Skills，但**没有沉淀一个跨 Sprint、跨员工、可复制的派单节拍**。结果：每次开新 Sprint 都要重写规则，员工边界容易漂移，TASKS.md 容易堆积无主卡。

### Decision

把"3 员工持续交付节拍"沉淀为 `docs/plans/roadmap-3-employees.md`，作为 **Sprint S1 → S4 的派单依据**，并约束：

1. **员工 ↔ Skill 绑定**：Cursor=Master(Product/Architecture/Review)，Windsurf=Backend+Frontend Skill，Codex=Test+Deployment+Documentation Skill。
2. **每张 task-card 只有一个 Owner Skill**，`Files owned` 必须精确到路径；越界即 Review 打回。
3. **并行的两张卡必须文件不重叠**；Master 在 TASKS.md DOING 列只能放不重叠的卡。
4. **5 行 handoff**（Changed / Verified / Risks / Next / Files）替代全量 diff 回传 Master，防止 Context 污染。
5. **Sprint 顺序**：S1 (M5 Archive) → S2 (M3.5 Ops，可与 S1 并行) → S3 (M6 Auth，强串行) → S4 (M7 候选 4 选 1)。

### Alternatives

1. 每次自由分配 — 已实践过，容易丢任务、漂移边界。
2. 单员工全栈 — 失去并行性，老板验收周期长。
3. 引入第 4 个 AI 员工 — 增加协调成本；不在当前预算内。

### Tradeoffs

- Pros：派单可复制；老板 1 行批准即可启动整 Sprint；Context 不爆。
- Cons：维护成本——roadmap + task-cards + TASKS.md 三处同步。

### Risks

- 员工"自行扩 Scope"——靠 `Files owned/avoided` + Review 打回兜底。
- 路线图与现实漂移——每个 Sprint DONE 后必须追加 §Retrospective 3 行。

### Follow-up

- [ ] 跑通 Sprint S1（M5）作为节拍样板
- [ ] S1 完成后在 roadmap 增 §Retrospective
- [ ] 若并行卡冲突 ≥ 2 次，重新评估边界粒度

## ADR-20260521-03: Commercial Auth Foundation — JWT + RBAC + Multi-Tenant-Ready Schema

Date: 2026-05-21
Status: Proposed → Accepted upon S1 (M5) DONE
Owner: Cursor (Master)

### Context

Intel Hub 目前完全无鉴权：任何能访问 `/api/v1/*` 的人都能 CRUD 来源、读全部文章、删告警。`REVIEW.md` 与 BACKLOG 一直挂着"商业 Auth 未定义"风险。M5 完成后即进入 S3 M6，本 ADR 必须先于代码。

### Decision

1. **机制：** JWT（HS256，对称密钥），`/auth/login` 同时签发 `access_token`（30 分钟）+ `refresh_token`（14 天）。
2. **前端存储：** `httpOnly` Cookie（`SameSite=Lax`，prod 必 `Secure`）。**禁止** localStorage，避免 XSS 窃取。
3. **CSRF：** 安全方法（GET/HEAD）免；非安全方法走 Cookie + `X-CSRF-Token` 双提交，token 由 `/auth/login` 返回 JSON Body。
4. **角色（RBAC v1）：** 三档 enum `user.role`：
   - `admin`：全部 CRUD + 用户管理 + 删源
   - `analyst`：读全部 + 写 sources/alerts + 触发 ingest
   - `viewer`：只读 briefing / articles / archives
5. **多租户预留：** 所有业务表（sources / articles / intelligence_reports / alerts / daily_archives）新增 `tenant_id VARCHAR(64) NOT NULL DEFAULT 'default'` + 单列索引。v1 **不启用** RLS，仅留迁移路径。M6 后所有查询走 `current_user.tenant_id` 过滤（dependency 注入）。
6. **首管理员引导：** 启动时若 `users` 表为空且环境提供 `AUTH_BOOTSTRAP_ADMIN_EMAIL` + `AUTH_BOOTSTRAP_ADMIN_PASSWORD`，自动创建 `admin` 用户；否则启动时打印一次性命令提示。**禁止** 默认 admin/admin。
7. **密码：** bcrypt（passlib，rounds=12）。最小长度 12。
8. **公开端点白名单：** `/health`、`/ping`、`/docs`、`/openapi.json`、`/auth/{login,refresh,logout}`。其余一律 401 未授权。
9. **`/briefing` 与 `/archives` 在 dev/prod 行为：** 由 `AUTH_BRIEFING_PUBLIC` 控制，默认 dev=true / prod=false。CI 必须显式覆盖。
10. **审计：** `auth_events` 表记录 login_success / login_failed / refresh / logout，含 IP + UA。M6 v1 不做异常检测，仅落库。

### Alternatives

1. **Session + Server-side store**（Redis）：状态复杂度↑，撤销简单；权衡后 v1 选 JWT，撤销靠短期 access + 黑名单 refresh。
2. **OAuth2/OIDC（Auth0/Clerk）**：商业可分发更易，但绑定外部供应商 + 增加成本；推到 M8 商业上架时再考虑。
3. **API Key only**：适合内部服务-to-服务，不适合人类用户；保留作为 v1.1 增量（service tokens）。
4. **延迟多租户列**：决策时未加 `tenant_id` → 后期回填 4000+ 文章成本高。今天加列只增一个默认值，零代价。

### Tradeoffs

- Pros：FastAPI 原生支持；前端 cookie 体验顺；JWT 横向扩展；多租户列零迁移成本。
- Cons：refresh 撤销需要黑名单（Redis SET，TTL = refresh 寿命）；JWT secret 泄漏需重签全员（rotate kid）。

### Risks

- JWT_SECRET 弱：CI 强制 ≥ 32 字符随机。
- 前端 401 自动 refresh 死循环：refresh 失败后必跳 `/login`，不重试。
- 公开 `/briefing` 在 prod 误开：CI lint `AUTH_BRIEFING_PUBLIC` 在 `docker-compose.prod.yml` 必须 false。
- 老旧 dashboard 数据无 `tenant_id`：迁移 DEFAULT `'default'`，应用层永远显式过滤。

### Follow-up

- [ ] M6-A 实现 User 表 + JWT 签发
- [ ] M6-B 给 sources/articles/alerts/archives 加 `current_user` 依赖
- [ ] M6-C 前端登录页 + AuthProvider
- [ ] M6-D 测试 + 部署 + 文档
- [ ] M8 评估 OIDC 接入 + 多租户 RLS

## ADR-20260521-04: M7-A 双语简报（中文化海外资讯）

Date: 2026-05-21
Status: Proposed（M7 候选 · 由老板批准激活）
Owner: Cursor (Master)

### Context

海外源（OSINT / BestBlogs-EN / RSSHub-X 英文）占比 60%+，老板每日简报英文段落多，认知成本高。`/briefing` 与 `/archives` 都展示原文 + 原始摘要。

### Decision

在 `intelligence_reports` 表新增 `summary_zh TEXT` + `title_zh VARCHAR(512)` 两列；Celery 任务 `translate_report` 在 `analyze_article` 后链式调用，调用 `services/ai/translate.py`（OpenAI 优先，未配置 KEY 走 mock 标注 `[ZH-MOCK]`）。前端 `/briefing` 与 `/archives/{date}` 增"中/英"切换；默认中文。

### Alternatives

1. 调用机器翻译 API（DeepL/Google）：依赖外部 + 计费复杂；v1 复用 OpenAI 同 KEY。
2. 全部翻译标题 + 全文：成本爆炸 4000+ 篇；v1 只翻 `intelligence_reports.summary`（已过 AI 浓缩，平均 200 字）。
3. 前端实时翻译（浏览器 LLM）：质量不可控。

### Tradeoffs

- Pros：复用现有 AI 管线，2 列 + 1 任务即可；老板体验提升明显。
- Cons：OpenAI 配额翻倍；mock 模式翻译质量差。

### Risks

- 翻译错误传播：UI 标注 "AI 翻译" + 提供"看原文"按钮。
- 历史报告无中文：v1 不回填；新报告起算，老报告按需触发。

### Follow-up

- [ ] 激活后写 M7-A-1/A-2/A-3 卡

## ADR-20260521-05: M7-B Setup Wizard（5 分钟跑起来）

Date: 2026-05-21
Status: Proposed（M7 候选）
Owner: Cursor (Master)

### Context

新用户/客户拿到代码到看到第一个简报需要：clone → 配 `.env` → docker compose → alembic → 跑 seed → 等 Beat 触发简报。门槛 30+ 分钟，且容易漏 `OPENAI_API_KEY` / `FEISHU_WEBHOOK_URL`。

### Decision

实现一次性 **Setup Wizard**：

1. 后端 `/api/v1/setup/{status,env,seed,bootstrap-admin,trigger-briefing}`，仅当 `users` 表为空时开放（M6 admin bootstrap 钩子里启用）。
2. 前端 `/setup`（无需登录路由），4 步：① 检测 DB/Redis ② 写 `.env`（前端表单 → 后端写 `backend/.env`） ③ 选择导入 seeds（多选 checkbox） ④ 创建首管理员 → 跳 `/login`。
3. Wizard 完成后写 `system_settings.setup_completed_at`，再访问 `/setup` 自动重定向 `/login`。

### Alternatives

1. 纯 CLI `make bootstrap`：开发者向；不适合"小团队商业分发"。
2. Docker image 内嵌默认 admin：安全灾难。
3. Notion 模板 + 人工对话：不可扩展。

### Tradeoffs

- Pros：把"商业分发"从"会读 README"降到"会点按钮"。
- Cons：写 `.env` 文件权限敏感；需要明确文档"仅本地/可信网络使用 Wizard"。

### Risks

- `/setup` 在已 setup 系统被打开：服务端 hard-check `users` 表为空 + `setup_completed_at IS NULL`。
- 写 `.env` 暴露 secrets：写完后 chmod 600。

### Follow-up

- [ ] 依赖 M6 完成（共享 admin bootstrap）
- [ ] 激活后写 M7-B-1/B-2/B-3 卡

## ADR-20260521-06: M7-C AI 成本守门（限额 / 队列优先级 / mock 透明）

Date: 2026-05-21
Status: Proposed（M7 候选 · 推荐优先级最高）
Owner: Cursor (Master)

### Context

`OPENAI_API_KEY` 一旦在 prod 配置，4000+ 文章 × 后续日增 200+，单日可能跑出数十美元成本，且没有保护。`REVIEW.md` 一直挂"`OPENAI_API_KEY` production strategy"。

### Decision

引入 **AI Budget Layer**：

1. 配置：`AI_DAILY_TOKEN_BUDGET`（默认 200_000 token）+ `AI_MONTHLY_TOKEN_BUDGET` + `AI_MODEL`（默认 gpt-4o-mini）。
2. 新表 `ai_usage_events`：记录 task_id / model / prompt_tokens / completion_tokens / cost_usd / created_at。
3. `services/ai/client.py` wrap：每次调用前查日预算/月预算；超额降级 mock + 写入 `ai_usage_events.status='budget_exceeded'`。
4. Celery 任务优先级：briefing/archive > alert match > backfill analyze（用 Celery `Queue` 分级 + `prefetch_multiplier=1`）。
5. 前端 `/settings/ai-usage`：日/月用量图 + 当前模型 + 余额提示（admin only）。
6. mock 透明：任何 mock 响应都在 `intelligence_reports.ai_mode` 字段标记 `mock|budget_exceeded|live`，UI 显式徽章。

### Alternatives

1. 不限额，靠 OpenAI dashboard 监控：事后才知道，已超支。
2. 强行限流（QPS）：不解决总量问题。
3. 切到本地 LLM：另一个 ADR 决策，不在本卡。

### Tradeoffs

- Pros：可预测成本；商业部署前置必备。
- Cons：超额降级会让简报质量下降，UI 必须诚实告知。

### Risks

- 用量计算误差（OpenAI 返回 token 数）：以 API 返回为准；偏离用 `usage_correction` 字段。
- 月预算重置时区：以 `AI_BUDGET_TIMEZONE`（默认 Asia/Shanghai）月初为界。

### Follow-up

- [ ] 激活后写 M7-C-1/C-2 卡

## ADR-20260521-07: M7-D Postgres 全文检索（先 tsvector，不引入 ES）

Date: 2026-05-21
Status: Proposed（M7 候选）
Owner: Cursor (Master)

### Context

文章 4000+ 且日增 200+，但 `/articles` 只能按来源/标签/日期过滤；用户问"上周二关于 OpenAI 的报道有哪些"需要肉眼翻页。BACKLOG 一直挂"Full-text search"。

### Decision

用 PostgreSQL 原生 `tsvector` + `GIN` 索引，**不引入 Elasticsearch**：

1. 给 `articles` 增 `search_vector tsvector GENERATED ALWAYS AS (setweight(to_tsvector('simple', coalesce(title,'')), 'A') || setweight(to_tsvector('simple', coalesce(summary,'')), 'B') || setweight(to_tsvector('simple', coalesce(content_text,'')), 'C')) STORED`。
2. 索引 `GIN(search_vector)`。
3. API `/api/v1/articles?q=...&lang=zh|en|simple`，使用 `websearch_to_tsquery`。
4. 中文：v1 用 `'simple'` 配置（按空格/标点切词，对英文友好；中文检索召回率有限）；v1.1 评估 `zhparser` 扩展（需 PG 安装包，列入 follow-up）。
5. 排序：`ts_rank_cd(search_vector, query) DESC`。
6. 前端 `/articles` 顶部增搜索框；高亮命中片段（Postgres `ts_headline`）。

### Alternatives

1. Elasticsearch：运维成本高，单机部署 8GB+ 内存。
2. Meilisearch：轻量但是要单独服务进程 + 索引同步。
3. 仅 LIKE 查询：4000+ 文章 + 长 content 时延上百毫秒。

### Tradeoffs

- Pros：零新服务；现有 Docker compose 不变；GIN 索引在中等数据量上够快。
- Cons：中文召回率不如 zhparser/ES；长文 content 占 GIN 空间（评估后可改只索引 title+summary）。

### Risks

- GIN 索引膨胀：M7-D 实现完后跑 `pg_stat_user_indexes`，若 size > 50% table size 切到 title+summary。
- 慢查询：`q` 中包含极常见词时 plan 退化；UI 限制 ≥ 3 字符再触发。

### Follow-up

- [ ] 激活后写 M7-D-1/D-2/D-3 卡
- [ ] v1.1 评估 zhparser
