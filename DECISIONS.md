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
- [x] Resolve duplicate ADR locations (`DECISIONS.md` vs `docs/decisions.md`) — see ADR-20260521-03.

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
Status: Accepted
Owner: Cursor (Master)

### Context

Daily briefing is computed on-the-fly; no day-boundary snapshots exist. Operators cannot compare metrics or re-read past Top-N digests as the corpus grows (4000+ articles). Commercial Edition requires day-boundary auditability and category-level trend visibility, not MVP-only live briefing.

### Decision

Add **Archive Layer**: table `daily_archives` with per-calendar-day `briefing_json` + `metrics_json`.

- **Calendar:** `archive_date` uses `ARCHIVE_TIMEZONE=Asia/Shanghai` (北京时间).
- **Snapshot task:** Celery `archive_daily_snapshot` after daily briefing (Beat 06:15 UTC); UPSERT per day; `scripts/backfill-archives.py` for history.
- **Metrics v1:** `metrics_json.category_heat[]` per `sources.category`; `heat_score = articles + 3×high_relevance + avg_relevance`.
- **API:** `GET /api/v1/archives`, `/archives/{date}`, `/archives/trends/category-heat?days=30`.
- **UI:** `/archives` (list + day detail), `/trends` (category heat over 7/14/30 days).
- **List performance:** archive list queries defer `briefing_json` load (summary-only).

### Alternatives

1. Briefing JSON only — no structured trends.
2. Metrics only — no historical readable digest.
3. Export articles to cold storage — heavier, deferred to M5.1.

### Tradeoffs

- Pros: Fast trend queries; preserves readable history; minimal change to existing tables; business-category heat aligns with taxonomy.
- Cons: JSON row growth; timezone semantics must be documented; implementation ahead of Codex sign-off requires REVIEW gate.

### Risks

- Beat ordering vs briefing task — mitigate with 15min offset or task chain.
- Large `briefing_json` — cap at Top 20 items; list API must not SELECT full JSON.
- Dev port 8000 zombie processes — use `8001` in `dev.ps1` / Next rewrite until port cleared.

### Follow-up

- [x] Approve `docs/plans/M5-daily-archive-trends.md`
- [x] Windsurf Phase A–C (landed; pending Codex M5-D)
- [x] Update PRD scenario 10 (archives/trends)
- [ ] Codex M5-D: pytest + acceptance + `docs/api.md` sync + Review verdict

## ADR-20260521-02: Three-Employee Delivery Cadence (Cursor / Windsurf / Codex)

Date: 2026-05-21
Status: Accepted
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

- [x] 跑通 Sprint S1（M5）作为节拍样板 — M5-D live smoke ALL PASS 2026-05-22
- [ ] S1 完成后在 roadmap 增 §Retrospective
- [ ] 若并行卡冲突 ≥ 2 次，重新评估边界粒度

## ADR-20260521-03: ADR Authority Source (Root DECISIONS.md)

Date: 2026-05-22
Status: Accepted
Owner: Cursor (Master)

### Context

Repository had two decision locations: root `DECISIONS.md` (ADR template + numbered ADRs) and `docs/decisions.md` (early bootstrap notes). Agents could write new ADRs to the wrong file, causing drift (`REVIEW.md` Documentation Risk).

### Decision

1. **Authoritative ADR registry:** root `/DECISIONS.md` only. All new ADRs use `ADR-YYYYMMDD-NN` format in this file.
2. **`docs/decisions.md`:** redirect stub pointing to root; historical bootstrap notes moved to `docs/decisions-archive.md`.
3. **Cross-references:** `AGENTS.md`, `ARCHITECTURE.md`, task-cards, and plans reference `DECISIONS.md` — not `docs/decisions.md` — for architecture decisions.
4. **Runtime prompts:** `prompts/` YAML remains separate from ADR docs (see `REVIEW.md` AI Collaboration Risks).

### Alternatives

1. Keep dual files with sync discipline — rejected; already failed in practice.
2. Delete `docs/decisions.md` — rejected; breaks old links; archive + redirect preferred.
3. Move all ADRs under `docs/` — rejected; `AGENTS.md` already standardizes root `DECISIONS.md`.

### Tradeoffs

- Pros: Single source of truth; Review can grep one file; matches Commercial Edition governance.
- Cons: One-time migration of legacy notes; old PR links need redirect header.

### Risks

- Stale references to `docs/decisions.md` in external docs — mitigate with redirect + archive.

### Follow-up

- [x] Redirect `docs/decisions.md`
- [x] Archive legacy notes to `docs/decisions-archive.md`
- [x] Close REVIEW.md duplicate-ADR item
