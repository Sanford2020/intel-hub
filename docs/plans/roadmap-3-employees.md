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

## 1. 总览：四个 Sprint + UI 插队 Sprint

| Sprint | 主题 | 里程碑 | 主力员工 | 估算大小 |
|--------|------|--------|----------|----------|
| **S1 · M5** | Daily Archive & Trends（已规划，立即开工） | 历史归档 + 趋势页 | Windsurf 主力 · Codex Review | 中 |
| **S1.5 · M5.5** | Frontend Intelligence Workbench Redesign | 专业情报工作台 + 统一 UI 系统 | Windsurf Frontend · Codex QA · Cursor Review | 中 |
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

## 2.5 Sprint S1.5 · M5.5 Frontend Intelligence Workbench Redesign

**状态：** 规划完成（见 `docs/plans/M5.5-frontend-intelligence-workbench-redesign.md`）
**目的：** 把页面从"功能堆叠型后台"升级为"专业情报分析工作台"。

### 派单顺序

```text
T0  Cursor    维护设计口径 + 最终 Review (UI-R)
T1  Windsurf  F1: navigation + mobile menu + shared components + dashboard homepage
T2  Windsurf  F2: briefing/articles/sources/alerts visual alignment
T3  Codex     QA: lint/type-check/build/test + route smoke + Review evidence
T4  Cursor    UI-R: verdict + TASKS.md 收口
```

| Task | 员工 | Files owned | Validation |
|------|------|-------------|------------|
| TASK-20260522-UI-F1 | Windsurf · Frontend | `apps/web/src/components/layout/AppNav.tsx`, `apps/web/src/components/ui/**`, `apps/web/src/components/intel/**`, `apps/web/src/app/globals.css`, `apps/web/src/app/layout.tsx`, `apps/web/src/app/page.tsx`, `apps/web/src/lib/format.ts`, `apps/web/src/lib/intel-ui.ts`, `apps/web/src/lib/intel-labels.ts`, `apps/web/src/stores/theme.ts` | `npm run type-check && npm run build && npm run test:run`; mobile nav works |
| TASK-20260522-UI-F2 | Windsurf · Frontend | `apps/web/src/app/briefing/page.tsx`, `apps/web/src/app/articles/**`, `apps/web/src/app/sources/page.tsx`, `apps/web/src/app/alerts/page.tsx`, `apps/web/src/app/archives/**` and `apps/web/src/app/trends/**` only after M5-C stable | same frontend validation; route smoke for briefing/articles/sources/alerts |
| TASK-20260522-UI-QA | Codex · Test/Review | `apps/web/__tests__/**`, `REVIEW.md`, `docs/operations/frontend-ui-qa-2026-05.md` | `npm run lint && npm run type-check && npm run build && npm run test:run`; Review verdict recorded |
| TASK-20260522-UI-R | Cursor · Review | `TASKS.md`, `REVIEW.md`, optional plan retrospective | Review verdict APPROVE / REQUEST_CHANGES / BLOCK |

**禁止跨边界：**

- F1 不改 `apps/web/src/app/archives/**`、`apps/web/src/app/trends/**`，避免与 M5-C 冲突。
- Windsurf 不改 `backend/**`、`workers/**`、`services/**`。
- Codex 不修业务 UI；发现问题写 Review finding 或开 follow-up。

**老板验收：**

1. 首页第一屏是今日情报工作台：指标、Top 情报、系统状态、行动入口。
2. 手机宽度下能进入所有核心页面。
3. 简报、资讯、来源、告警视觉统一，深色模式可用。
4. `npm run type-check && npm run build && npm run test:run` 全绿。

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

**触发条件：** S1 (M5) DONE，且老板表态愿意把 Hub 让外部账号使用。

> 这一步把 `REVIEW.md` 里"商业 Auth 未定义"和 BACKLOG "Commercial auth ADR" 一起结清。**先 ADR 再代码。**

### Phase 排序（强串行）

```text
M6-ADR  Master  写鉴权 ADR + 任务拆解
  └─→ M6-A  Windsurf Backend  User / Session / JWT scaffold
  └─→ M6-B  Windsurf Backend  保护现有 /api/v1 路由 + RBAC
        └─→ M6-C Windsurf Frontend  登录页 + 受保护路由 + 401 处理
              └─→ M6-D Codex  测试 / 部署 / 文档
```

| Task ID | 员工 | Owner Skill | 关键交付 |
|---------|------|-------------|----------|
| TASK-20260601-M6-ADR | Cursor | Architecture | `DECISIONS.md` ADR：JWT vs Session、单租户 vs 多租户、`OPENAI_API_KEY` 是否对租户透明 |
| TASK-20260601-M6-A | Windsurf · Backend | Backend Skill | `backend/app/modules/auth/**`、`alembic` 用户表迁移、`/api/v1/auth/{login,logout,me}` |
| TASK-20260601-M6-B | Windsurf · Backend | Backend Skill | FastAPI dependency `current_user`，给 sources/articles/alerts 加保护；管理员-only 接口标注 |
| TASK-20260601-M6-C | Windsurf · Frontend | Frontend Skill | `/login`、`AuthProvider`、`apps/web/middleware.ts` 路由守卫、401 跳转 |
| TASK-20260601-M6-D | Codex | Test + Deployment + Documentation | `tests/test_auth.py`、`docs/api.md` 鉴权章节、`docs/deployment.md` JWT secret 配置、`docker-compose` 注入 `JWT_SECRET` |

**老板验收：** 公网部署后未登录访问 dashboard → 跳 `/login`；管理员能创建用户；分析师只读。

## 5. Sprint S4 · M7 Stickiness Phase 2（四选一）

S3 收尾后，老板需要在以下四个方向中**择一**作为 M7，避免 scope creep。Master 不替老板做选择，但给出推荐顺序：

| 候选 | 主要价值 | 估算 | 主力员工 |
|------|----------|------|----------|
| **A. 双语简报** | 海外信息中文化，老板每日体验提升 | 小 | Windsurf Backend（翻译管线）+ Codex |
| **B. Setup Wizard** | 新用户 5 分钟跑起来，商业可分发 | 中 | Windsurf Backend + Frontend |
| **C. AI 成本守门** | 真实 `OPENAI_API_KEY` 上线前的护栏（限额 / 队列优先级 / mock fallback 透明) | 小 | Windsurf Backend + Codex |
| **D. Postgres 全文检索** | 4000+ 文章可搜，避免引入 ES | 中 | Windsurf Backend + Frontend |

**Master 推荐顺序：** C → A → B → D（先把生产风险盖住，再做易用性，最后做高级检索）。

## 6. BACKLOG（不进当前 Sprint）

- 多租户隔离与配额（M8+）
- Elasticsearch / 向量检索（M8+）
- 实体关系图（M9+）
- Mobile / 推送 App（M9+）
- 翻译质量评估 + 人工反馈环（M8+）

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
3. **Windsurf 可开 UI-F1** → `TASK-20260522-UI-F1` 只改导航、共享组件、首页 Dashboard，不碰 archives/trends。
4. **Master 不写代码**：本轮 Master 只负责审 M5-M ADR、S2 OPS-04 ADR-02、M5.5 UI-R。

---

**更新规则：** 本路线图由 Master 维护；每个 Sprint DONE 后追加 §Retrospective 一段（3 行）。
