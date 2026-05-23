# REVIEW.md

This file records initial project risks for follow-up. Per initialization rules, no business code was changed to fix these items.

## Architecture Risks

- ~~Commercial authentication and authorization are not yet defined in the current architecture docs.~~ **Partially resolved:** ADR-20260601-01 Accepted (2026-06-01); implementation pending M6-A→D.
- Production hosting target is not confirmed.
- Worker/beat 24-hour observation is not recorded, so long-running operational reliability remains unproven.
- Existing documentation exists in multiple locations (`PROJECT_BRIEF.md`, `docs/project/*`, `.multi-agent/*`), which can drift unless one source of truth is maintained.

## Code Quality Risks

- Repository currently appears to have many untracked files; baseline commit strategy should be clarified before multi-agent work.
- Some generated/runtime files appear near source areas, such as Celery beat schedule artifacts under `backend/`; confirm `.gitignore` coverage before committing.
- AI/mock behavior is useful for local development, but commercial behavior should clearly distinguish mock mode from real AI mode.

## Test Risks

- Backend tests pass in the current local environment; `scripts/validate_project.sh` and GitHub Actions CI now capture production-like checks (OPS-02).
- Frontend type-check/build pass, but end-to-end browser tests are not formalized.
- Worker/beat unattended runtime observation is pending; OPS-03 short-run evidence exists, but 24h sign-off is still blocked.

## Documentation Risks

- ~~Root `DECISIONS.md` now exists, while `docs/decisions.md` also exists~~ **Resolved (ADR-20260521-03):** root `DECISIONS.md` is authoritative; `docs/decisions.md` is redirect only.
- API docs are manually maintained and may drift from FastAPI routers if not checked during review — **M5-D must sync `docs/api.md` for archives endpoints.**
- Deployment docs need production-specific values once hosting target is selected.

## Deployment Risks

- Docker Compose depends on local env files; fresh setup must copy examples correctly.
- No production secrets management strategy is documented yet.
- Backup, monitoring, alerting, and log aggregation are checklist items but not implemented in docs.

## AI Collaboration Risks

- Multiple AI tools may edit overlapping files unless `TASKS.md` ownership is kept current — **M5 implementation landed before M5-M Accepted; enforce ADR-before-code for future sprints.**
- **M5 + M5.5 parallel file boundaries:** largely resolved; remaining UI polish is F2-fix only. **M6-C** may touch `layout.tsx` — serialize with UI-F2-fix.
- Cursor, Windsurf, and Codex need clear prompts and review gates to avoid broad refactors.
- Structural issues should be recorded here first instead of silently fixed during unrelated tasks.
- `prompts/` contains both runtime YAML templates and AI-agent Markdown prompts; do not confuse the two.

## Commercial Delivery Risks (2026-05-22)

- **M5 Daily Archive & Trends:** **DONE (S1 closed 2026-05-22).** Live `acceptance-smoke.py --api http://127.0.0.1:8001` returned **ALL PASS** (4215 articles, 2 archive rows, 9 trend categories). Remaining: archive `partial` semantics (P1, deferred) and ≥30d backfill for richer trends UX.
- **Mock AI default:** empty `OPENAI_API_KEY` → `ai_mode=mock`; commercial demos must disclose; M7-C (cost guard) recommended before public deploy.
- **Auth (M6):** ADR-20260601-01 — **APPROVE** (M6-A→D done; live smoke PASS).
- **Archive backfill depth:** trends UX needs ≥7 days backfill; ops must run `backfill-archives.py --days 30` after deploy.
- **M5.5 UI workbench:** F1 **DONE**；F2 视觉合流 **大部分完成**（Codex F2 QA 2026-05-22）。**未签收：** 390px `/articles` 横向 overflow；首页 drawer 打开后 overflow；`/trends` duplicate React key。公网演示前需 UI-F2-FIX + QA-RECHECK APPROVE。

## M5-D Archive Review (2026-05-22)

Verdict: **APPROVE** — M5-A/B/C/D move to DONE. Automation and live acceptance smoke both pass against Postgres-backed API on `:8001`.

### Findings

- ~~**P0: Required validation command `pytest -q` fails from repo root.**~~ Resolved (`pytest.ini` + `PROMPTS_DIR`). **80 passed.**
- ~~**P0: Live acceptance smoke cannot complete.**~~ Resolved 2026-05-22: Docker db/redis healthy; `acceptance-smoke.py --api http://127.0.0.1:8001` → **ALL PASS** (ingest 6 sources, briefing 24h, archives 2 rows, trends 9 categories).
- **P1 (deferred): Archive failure semantics** — upstream briefing failure → `status="partial"` not implemented; current behavior writes `failed` and re-raises. Non-blocking for S1 sign-off; track as M5.1 or accept as-is.
- **P2 (optional):** `briefing_json` p95 / metrics SQL EXPLAIN not measured; backfill only 2 days — run `backfill-archives.py --days 30` for production trends UX.

### Verification

- `pytest -q` from repo root: **PASS**, 80 passed.
- `python scripts/acceptance-smoke.py --api http://127.0.0.1:8001`: **PASS**, ALL PASS.
- Archive API live: **PASS** — 2 recent rows, timezone OK, 9 category heat series.
- `docs/api.md`: **SYNCED** with archives/trends contract.

## M5.5 UI-QA — F2 Recheck (2026-05-22)

Verdict: **REQUEST_CHANGES** (Codex)

### Passed

- `npm run lint` / `type-check` / `build` / `test:run`: **PASS**
- Workbench homepage、briefing/trends/archives 新 shell、友好错误态、390px 移动菜单可打开、暗色可读
- 路由 smoke：无 framework overlay、无 raw `Internal Server Error`
- Backend boundary: **PASS** for UI-F2 scope

### Blockers (must fix before APPROVE)

| ID | Severity | Issue | Owner |
| --- | --- | --- | --- |
| UI-F2-01 | P1 | 390px horizontal overflow — `/articles` filters; `/` after drawer open (`scrollWidth` > viewport) | Windsurf |
| UI-F2-02 | P2 | `/trends` duplicate React key `2026-05-20` in trend cards/table | Windsurf |

Evidence: `docs/operations/frontend-ui-qa-2026-05.md`

## M5.5 UI-R — Master Review (2026-05-22)

Verdict: **APPROVE** — F2-FIX recheck 2026-05-23; prior REQUEST_CHANGES blockers resolved.

### Windsurf F2 handoff assessment

- **Scope:** briefing, articles, sources, alerts, archives, trends updated to shared `PageHeader` / design system — **substantially complete** vs prior F1-only PASS.
- **No formal handoff file** under `.multi-agent/handoffs/`; QA report + code inspection (`PageHeader` in briefing/trends) used as evidence.
- **File boundary:** no backend/API diff attributed to UI-F2; residual `workers/tasks/archives/__init__.py` belongs to OPS-03 — exclude from UI verdict.

### Master checklist (partial)

| Item | Result |
| --- | --- |
| F1 did not pre-empt unstable M5-C | PASS (historical) |
| F2 unified core pages | PASS |
| Dashboard operational first screen | PASS |
| Mobile nav exists | PASS |
| Mobile layout no overflow | **FAIL** (P1) |
| Dark mode readable | PASS |
| Codex validation complete | PASS with findings |

**Next:** `TASK-20260522-UI-F2-fix` → Codex QA recheck → UI-R APPROVE.

## M5.5 UI-QA — F1 Baseline (2026-05-22, superseded for sign-off)

Verdict: **PASS (F1 scope only)** — superseded by F2 recheck above for commercial sign-off.

## M6 Auth — Implementation Review (2026-06-01)

Verdict: **APPROVE**

### Verified

- `pytest -q`: **91 passed**
- `npm run type-check && build`: **PASS**
- Live `acceptance-smoke.py --api http://127.0.0.1:8001`: **ALL PASS** (with auth login)
- Browser: login → workbench; 390px `/articles` + drawer — no horizontal overflow

### Notes

- Middleware excludes `/api/*` so Next.js rewrite proxy can reach backend login.
- Scripts use `SMOKE_EMAIL` / `SMOKE_PASSWORD` (default `admin@example.com` / `change-me`).

## M6 Auth — Pre-Implementation Risks (2026-06-01)

ADR-20260601-01 Accepted; no business code yet.

- **P1:** M6-B will break unauthenticated scripts (`seed-sources.py`, ingest helpers) until M6-D adds login step.
- **P1:** Full pytest suite needs auth fixtures — budget time in M6-D, not M6-A alone.
- **P2:** M6-C may conflict with UI-F2 on `layout.tsx` / `AppNav.tsx` — Master must serialize or split file ownership.
- **P2:** Celery workers remain outside HTTP auth; rely on network isolation for worker processes.
- **Out of scope confirmed:** multi-tenant billing, SSO, OAuth, invite flow — do not expand M6.

## Operational Risks (Sprint 6 Observations)

- **Sync batch ingest blocks API** for minutes when many RSS sources are ingested synchronously; use `?async=1` or `batch-ingest-rss.py --async`.
- ~~**Many Tier-0 RSS feeds fail** from local network (BBC/CNN timeout, Reuters 404, AP invalid XML)~~ **OPS-01 probed 2026-05-22:** `docs/operations/rss-health-2026-05.md` generated; failed enabled RSS rows were marked `enabled=false` in seeds. Remaining risk: results are localnet-only and RSSHub X requires a running local RSSHub service, so production/staging should rerun the probe before permanent source removal.
- **Celery Worker/Beat are not always running** in dev; articles/reports will not grow without them.
- **OPS-03 short-run finding:** Worker/Beat task registration is fixed and short-run dispatch worked, but 24h sign-off is still blocked because Celery inspect timed out locally and queue depth grew under the Windows solo worker (`default` queue ended at 623).
- **Worker autodiscovery** previously missed analyze/alerts tasks when `__init__.py` did not import modules; regression risk if new task packages omit imports.
- **Mock AI mode** is active when `OPENAI_API_KEY` is empty; commercial demos must label mock vs real output.

## Context Risks

- Long chat sessions without TASK updates lose Scope boundaries.
- Pasting full worker logs into Master context reduces planning quality.
- Duplicate docs (`ARCHITECTURE.md` / `docs/architecture.md`) — ADR path resolved via ADR-20260521-03.
- `prompts/` mixes runtime YAML (AI analysis) with Skill Markdown — agents must not edit YAML during bootstrap tasks.

## Long-term Maintenance Risks

- No formal E2E browser suite.
- RSS feed list requires ongoing curation as URLs rot.
- Commercial auth undefined — **ADR accepted; code pending M6-A→D** (see ADR-20260601-01).
- Production hosting target unknown.

## Follow-up Recommendations

- ~~Create a validation script task.~~ Done: OPS-02 (`validate_project.sh` + CI).
- ~~Create a commercial auth architecture task — M6-ADR pending (S3).~~ Done: ADR-20260601-01 + M6 task cards. Next: dispatch M6-A.
- Record a worker/beat observation task — OPS-03 short-run completed; 24h run still pending.
- ~~Decide whether root `DECISIONS.md` supersedes `docs/decisions.md`.~~ Done: ADR-20260521-03.
