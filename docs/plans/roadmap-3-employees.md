# Intel Hub — 3 AI 员工多迭代路线图

> **Master:** Cursor · **Builder:** Windsurf · **Execution:** Codex  
> 日期：2026-05-21 · 维护：Cursor (Master)  
> 配套：`AGENTS.md`、`SKILLS.md`、`workflows/autonomous-delivery.md`

## 0. 操作模式回顾

| 员工 | 工具 | 绑定 Skill | 默认产出 |
|------|------|------------|----------|
| **Master** | Cursor | Product / Architecture / Review | TASK 拆解、ADR、Review、合并方向 |
| **Builder** | Windsurf | Frontend Skill / Backend Skill | 业务代码（API / UI / Worker / Migration） |
| **Execution** | Codex | Test / Debug / Deployment / Documentation | pytest、acceptance、Docker、env、文档机械同步 |

**核心铁律：**

1. **先 TASK 后代码** — 无 `TASKS.md` 条目不允许动业务代码。
2. **一卡一员工** — 每张 task-card 只有一个 Owner Skill；并行任务的 `Files owned` 不得重叠。
3. **最小 Context** — Skill 会话只看本卡 `Scope` + `Files`，不要全仓库扫描。
4. **Master 不写业务代码** — Cursor 只做 ADR、TASKS、Review，除非老板明确指令。
5. **每张卡必带 Validation** — Codex 才有验收口径。
6. **5 行摘要回传** — Skill 完成后用 `Changed / Verified / Risks / Next / Files` 5 行回到 Master，不要把全量 diff 塞进 Master Context。

## 1. 总览：四个 Sprint

| Sprint | 主题 | 里程碑 | 主力员工 | 估算大小 |
|--------|------|--------|----------|----------|
| **S1 · M5** | Daily Archive & Trends（已规划，立即开工） | 历史归档 + 趋势页 | Windsurf 主力 · Codex Review | 中 |
| **S2 · M3.5** | Ops Closure（与 S1 并行可做） | 24h 观测 + 源治理 + CI | Codex 主力 · Master 1 张文档卡 | 小 |
| **S3 · M6** | Commercial Auth Foundation | 登录 + 鉴权 + 公网安全基线 | Cursor ADR → Windsurf B+F → Codex | 大 |
| **S4 · M7** | Stickiness Phase 2（候选） | 双语简报 / Setup Wizard / AI 成本守门 / 全文检索（**四选一**） | 视方向定 | 中 |

> 不再使用"周/天"工期。Master 一次只在 DOING 放 ≤ 3 张卡；老板验收靠每张卡的 `Validation`。

## 2. Sprint S1 · M5 Daily Archive & Trends

**状态：** 规划完成（见 `docs/plans/M5-daily-archive-trends.md` + ADR-20260521-01）  
**立即可派单。**

### 派单顺序

```text
T0  Master  写 ADR + 看板 (M5-M)
T1  Windsurf Backend  A1→A5 (data + Celery)
T2  Windsurf Backend  B1→B4 (API)
T3  Windsurf Frontend C1→C4 (UI)        ← 与 T2 串行（依赖 API schema）
T4  Codex             D1→D5 (test + ops + review)
```

| Task | 员工 | Files owned | Validation |
|------|------|-------------|------------|
| TASK-20260521-M5-M | Cursor | `DECISIONS.md`, `docs/prd.md`, `TASKS.md` | ADR Accepted + PRD scenario 10 写入 |
| TASK-20260521-M5-A | Windsurf · Backend | `backend/app/models/daily_archive.py`, `backend/app/modules/archives/**`, `backend/alembic/versions/*archives*.py`, `workers/tasks/archives/**`, `workers/celery_app.py`, `scripts/backfill-archives.py` | `alembic upgrade head` 成功；手动跑 task DB 多一行；重复幂等 |
| TASK-20260521-M5-B | Windsurf · Backend | `backend/app/modules/archives/router.py`, `backend/app/modules/archives/schemas.py`, `backend/app/api/v1/api.py`（仅 include_router）, `docs/api.md` | `curl /api/v1/archives` 200；`/trends?days=30&metric=articles_created` 返回 points |
| TASK-20260521-M5-C | Windsurf · Frontend | `apps/web/src/app/archives/**`, `apps/web/src/app/trends/**`, `apps/web/src/lib/intel-api.ts`（仅追加 archives/trends 封装）, `apps/web/src/components/Sidebar*`（导航追加） | `npm run type-check && npm run build` 绿；浏览器看到列表 + 折线 |
| TASK-20260521-M5-D | Codex | `backend/tests/test_archives.py`, `scripts/acceptance-smoke.py`, `run-daily-intel.ps1`, `docs/deployment.md`, `REVIEW.md` | `pytest tests/test_archives.py -q` 全绿；acceptance 通过；Review 报告无 BLOCK |

**禁止跨边界：**

- Windsurf Backend **不要** 改前端文件；Windsurf Frontend **不要** 改 `backend/`、`workers/`。
- Codex **不要** 改业务实现，只补测试 / 验收脚本 / 文档。

**老板验收：**

1. 跑一晚 Beat 后访问 `/archives` 看到昨天的简报快照。
2. `/trends?days=30&metric=articles_created` 返回 ≥ 1 个点（backfill 之后 ≥ 7）。
3. `pytest tests/ -q` 全绿。

## 3. Sprint S2 · M3.5 Ops Closure（与 S1 并行）

**目的：** 不阻塞 S1，把"久拖未结"的运营债务清掉。Codex 是天然主力。

| Task ID | 员工 | 标题 | Files owned | Validation |
|---------|------|------|-------------|------------|
| TASK-20260521-OPS-01 | Codex · Test | RSS 源健康清单 v2 | `seeds/**`（仅 disabled 标记）、`docs/operations/rss-health-2026-05.md`、`REVIEW.md` 条目 | 跑 `scripts/batch-ingest-rss.py --async --dry-run` 输出失败清单，提交报告 |
| TASK-20260521-OPS-02 | Codex · Deployment | `validate_project.sh` + GitHub Actions CI | `scripts/validate_project.sh`（新建 bash 等价于 `.ps1`）、`.github/workflows/ci.yml`、`docs/deployment.md` CI 章节 | PR push 后 GH Actions：pytest + npm build + docker compose config 全过 |
| TASK-20260521-OPS-03 | Codex · Test | Worker / Beat 24h 观测落档 | `docs/operations/worker-observation-2026-05.md`、`backend/tests/test_e2e_ingest_analyze.py`（如需补） | 报告含：起止时间 / 来源数 / 文章增量 / 报告增量 / 告警事件 / 失败列表 |
| TASK-20260521-OPS-04 | Cursor · Documentation | `DECISIONS.md` 与 `docs/decisions.md` 权威性定夺 | `DECISIONS.md`（增 ADR-20260521-02）、`docs/decisions.md`（写明 redirect） | 仓库只有一个 ADR 权威源；`REVIEW.md` 中"重复 ADR"风险关闭 |

**并行规则：** S1 用 `backend/app/modules/archives/**`、`apps/web/src/app/archives/**`、`workers/tasks/archives/**`；S2 用 `scripts/`、`docs/operations/`、`.github/workflows/`、`seeds/`。**文件边界不重叠**，可并行。

## 4. Sprint S3 · M6 Commercial Auth Foundation

**触发条件：** S1 (M5) DONE。  
**核心决策（ADR-20260521-03 Accepted upon S1 DONE）：** JWT (HS256) + httpOnly Cookie + CSRF 双提交；RBAC 三档 `admin/analyst/viewer`；多租户列 `tenant_id` 全表预留（v1 单租户 `default`）；首管理员 env 引导；bcrypt rounds=12；refresh 黑名单 Redis；公开白名单 `/health /ping /docs /openapi.json /auth/*`。

### Phase 排序（强串行）

```text
M6-ADR  Master   ADR Proposed→Accepted + PRD §11 + 修订下游卡（若需要）
  └─→ M6-A  Windsurf Backend  User + JWT + auth router + tenant 列迁移
        └─→ M6-B  Windsurf Backend  注入 current_user + tenant 过滤 + RBAC 矩阵
              └─→ M6-C Windsurf Frontend  /login + AuthProvider + middleware + RoleGate
                    └─→ M6-D Codex  鉴权测试 + RBAC 矩阵测试 + 部署文档 + CI 密钥校验
```

| Task ID | 员工 | Owner Skill | 关键交付 | 卡片 |
|---------|------|-------------|----------|------|
| TASK-20260601-M6-ADR | Cursor | Architecture | ADR Accepted + PRD §11 权限矩阵 | `.multi-agent/task-cards/TASK-20260601-M6-ADR.md` |
| TASK-20260601-M6-A | Windsurf · Backend | Backend Skill | `auth/**` + JWT + bootstrap admin + 多租户列迁移 | `TASK-20260601-M6-A.md` |
| TASK-20260601-M6-B | Windsurf · Backend | Backend Skill | 12 业务路由加保护 + RBAC 矩阵 + tenant_scoped_query 工具 | `TASK-20260601-M6-B.md` |
| TASK-20260601-M6-C | Windsurf · Frontend | Frontend Skill | `/login` + middleware + AuthProvider + RoleGate + 401 自动 refresh | `TASK-20260601-M6-C.md` |
| TASK-20260601-M6-D | Codex | Test+Deploy+Doc | `test_auth.py / test_rbac.py / test_tenant_isolation.py` + JWT_SECRET 校验 + docker-compose.prod | `TASK-20260601-M6-D.md` |

**老板验收：**
- 公网部署后未登录访问 dashboard → 跳 `/login`
- admin 创建 analyst/viewer 用户
- viewer 看 sources 但无删除按钮；尝试 DELETE 返回 403
- A 租户用户读不到 B 租户数据（虽然 v1 默认 `default` 单租户，列已就位）

## 5. Sprint S4 · M7 Stickiness Phase 2（四赛道全规划，老板按需激活）

**激活规则：** 老板把对应赛道的卡从 BACKLOG 移到 DOING（或一句话告知 Master）即可。每个赛道的 ADR 已写为 `Proposed`，激活时翻 `Accepted`。

**Master 推荐顺序：** C → A → B → D
- **C（AI 成本守门）** = prod 上线前置护栏，最高优先
- **A（双语简报）** = 体验提升，与 C 联动最自然
- **B（Setup Wizard）** = 商业分发前置
- **D（全文检索）** = 数据量到 8000+ 后真痛

四赛道**文件不重叠**，理论可并行（但建议串行以免 Master Context 过载）。

### 5.1 M7-A · 双语简报（中文化海外资讯）

**ADR：** ADR-20260521-04（Proposed）  
**核心决策：** `intelligence_reports` 增 `summary_zh/title_zh/translated_at`；Celery `translate_report` 链在 `analyze_article` 后；mock 模式打 `[ZH-MOCK]` 前缀；UI 默认中文 + "看原文"切换。

| Task ID | 员工 | 交付 |
|---------|------|------|
| TASK-20260615-M7A-1 | Windsurf · Backend | 迁移 + `services/ai/translate.py` + Celery 任务 + Schema |
| TASK-20260615-M7A-2 | Windsurf · Frontend | `LangToggle` + 3 路由接入 + `AITranslatedBadge` |
| TASK-20260615-M7A-3 | Codex | `test_bilingual.py` + 部署文档 + PRD 更新 |

**老板验收：** 打开 `/briefing` 默认看中文；点"看原文"切英文；旧报告显示"AI 翻译尚未生成"+ 英文兜底。

### 5.2 M7-B · Setup Wizard（5 分钟跑起来）

**ADR：** ADR-20260521-05（Proposed） · 依赖 S3 M6 完成  
**核心决策：** `/setup` 4 步引导仅当 `users` 表空时开放；后端写 `backend/.env` 后 chmod 600；引导完成写 `system_settings.setup_completed_at`，二次访问 403。

| Task ID | 员工 | 交付 |
|---------|------|------|
| TASK-20260615-M7B-1 | Windsurf · Backend | `setup/router.py` 5 个端点 + `system_settings` 表 + guards |
| TASK-20260615-M7B-2 | Windsurf · Frontend | `/setup` 4 步组件 + middleware 白名单 |
| TASK-20260615-M7B-3 | Codex | `test_setup.py` + README 快速开始改写 + deployment |

**老板验收：** fresh DB → 访问 `/setup` → 4 步走完 → 自动跳 `/login`；再访问 `/setup` 重定向 `/login`。

### 5.3 M7-C · AI 成本守门（Master 推荐最高优先）

**ADR：** ADR-20260521-06（Proposed）  
**核心决策：** `AI_DAILY_TOKEN_BUDGET` + `AI_MONTHLY_TOKEN_BUDGET` + `ai_usage_events` 表；超额降级 mock 并打 `ai_mode='budget_exceeded'`；Celery 队列分级 `briefing>analyze>translate>backfill`。

| Task ID | 员工 | 交付 |
|---------|------|------|
| TASK-20260615-M7C-1 | Windsurf · Backend | `services/ai/budget.py` + 用量表 + 队列分级 + `ai_mode` 列 + `/ai/usage` API |
| TASK-20260615-M7C-2 | Windsurf · Frontend + Codex | `/settings/ai-usage` + `AIModeBadge` + 测试 + 部署文档 |

**老板验收：** prod 配 `OPENAI_API_KEY` 后日预算 5 美元跑分析；超额自动降级 mock；admin 在 `/settings/ai-usage` 看到日/月用量。

### 5.4 M7-D · Postgres 全文检索（不引入 ES）

**ADR：** ADR-20260521-07（Proposed）  
**核心决策：** `articles.search_vector` 生成列 + GIN 索引；`websearch_to_tsquery` + `ts_rank_cd` + `ts_headline`；中文 v1 用 `simple` 配置（zhparser 列为 v1.1）。

| Task ID | 员工 | 交付 |
|---------|------|------|
| TASK-20260615-M7D-1 | Windsurf · Backend | 迁移生成列 + GIN + `/articles?q=...` + 高亮 |
| TASK-20260615-M7D-2 | Windsurf · Frontend | SearchBox + 高亮渲染 + URL 同步 + sanitize |
| TASK-20260615-M7D-3 | Codex | API 测试 + 注入安全测试 + 召回率人工评估报告 |

**老板验收：** `/articles` 顶部搜索 "OpenAI" → 命中文章 + 高亮 + 排序合理；评估报告说明中英文召回率差异。

## 6. BACKLOG（不进当前 Sprint）

### M8 · 商业上架（S3 + S4 完成后）

- 多租户 RLS 真正启用（依赖 M6 列）
- OIDC / SSO 接入（Auth0 / Clerk）
- API 限流 + 用户配额（依赖 M6 + M7-C）
- 商业计费层（Stripe / 国内支付）

### M9 · 数据深度

- 实体关系图
- 标签共现矩阵
- 主题聚类与趋势预测
- 翻译质量评估 + 人工反馈环

### M10 · 触达

- Mobile / 推送 App
- 邮件 digest
- Slack / 飞书机器人交互

### 一直被推迟的"非必要项"

- zhparser PG 扩展（如 M7-D 评估证明值得）
- 向量检索（pgvector 而非 ES）
- 冷存储归档到 S3

## 7. 工作节拍（持续运行的"老板模式"）

每个迭代环（Master 自动跑）：

```text
1. Master 读 TASKS.md → 选 TODO 最高优先级
2. Master 写 / 更新 task-card：Goal / Scope / Files / Owner Skill / Validation / Risks
3. 派给 Skill（Windsurf 或 Codex）— Master 复制 prompts/skill-*.md + 任务上下文
4. Skill 实现 → 5 行回传摘要 → Master Review（workflows/review-workflow.md）
5. Codex 跑 Validation；通过 → TASK = DONE，Master 写 3 行老板可见结果
6. 失败 → 转 BLOCKED 或拆子卡，循环
```

**老板可见输出（每轮 3 行）：**

```
Done: <TASK-ID> — <一句话结果>
Verify: <URL 或命令>
Next: <下一张卡 ID>
```

## 8. 派单 Prompt 模板（直接复制给 Windsurf / Codex）

```markdown
You are the <Backend|Frontend|Test|Deployment|Documentation> Skill for Intel Hub.
Master Agent (Cursor) assigns you ONE task. Do NOT expand scope.

Read FIRST:
- prompts/skill-<owner>.md
- docs/plans/roadmap-3-employees.md §<sprint>
- .multi-agent/task-cards/<TASK-ID>.md

Constraints:
- Files owned: <list>
- Files avoided: ALL OTHER FILES
- Validation: <command>

Deliverable (5-line handoff to Master):
Changed: <files>
Verified: <command output / PASS|FAIL>
Risks: <any>
Next: <suggested next card or NONE>
Files: <touched paths>
```

## 9. 风险与缓解

| 风险 | 缓解 |
|------|------|
| Windsurf 同一卡内自行扩 Scope | task-card `Files owned` 必须精确；越界一律 Review 打回 |
| Codex 修业务代码而非补测试 | Codex 卡 `Files avoided: backend/app/**, apps/web/src/**`（除指定文件）|
| 同一文件被两个员工竞争 | Master 在 TASKS.md DOING 列只能放不重叠的卡 |
| Master Context 膨胀 | 完成卡只保留 5 行摘要；细节回到 task-card 文件 |
| 老板未配置真实密钥 | `OPENAI_API_KEY` / `FEISHU_WEBHOOK_URL` 缺失 → 走 mock；M6 之前不暴露公网 |

## 10. 立刻可执行的下一步

1. **批准本路线图** → Master 把 M5 5 张卡从 TODO 移到 DOING（仅 M5-M、M5-A 同时进入；其余等依赖）。
2. **Codex 同步开 M3.5** → OPS-01/02/03 三张卡（与 M5 文件不重叠）。
3. **Master 不写代码**：本轮 Master 只负责审 M5-M ADR + S2 OPS-04 ADR-02。

---

**更新规则：** 本路线图由 Master 维护；每个 Sprint DONE 后追加 §Retrospective 一段（3 行）。
