# M5.5 UI Redesign QA — 2026-05

Verdict: REQUEST_CHANGES

## Recheck Scope

- Plan: `docs/plans/M5.5-frontend-intelligence-workbench-redesign.md`
- Task: `TASK-20260522-UI-QA`
- App URL: `http://127.0.0.1:3000`
- Browser: Codex in-app Browser
- Viewports: 390px, 768px, 1280px
- Backend state during smoke: offline (`127.0.0.1:8001` refused connection)
- Recheck focus: Windsurf fixes for the previous UI-QA `REQUEST_CHANGES`

Windsurf F1/F2 handoff summaries were not found under `.multi-agent/handoffs`; QA inferred delivered scope from the working tree and task cards.

## Recheck Summary

The UI-facing fixes from the previous review are verified: raw `Internal Server Error` text no longer appears, lint is clean, the mobile navigation is usable, dark mode is readable, and the requested route smoke matrix renders without framework overlays or horizontal overflow.

The recheck still cannot approve because the working tree contains backend/app ingest changes during a UI-QA review. QA did not modify these files, but UI-R should attribute or split them before approval.

## Findings

### P1 — Backend/app changes remain present in the UI QA working tree

- Files: `backend/app/modules/ingest/pipeline.py`, `backend/app/modules/ingest/trends_parser.py`
- Evidence: `git diff --name-status -- backend/app ...` reports `M backend/app/modules/ingest/pipeline.py`; `git status --short` also shows `?? backend/app/modules/ingest/trends_parser.py`.
- Why it matters: M5.5 UI-QA scope forbids backend/API/business-code changes. The UI fixes can be accepted functionally, but the merge boundary is still unclear.
- Suggested owner: UI-R / Master to attribute these backend changes to the proper task or split before merge.

### Residual — Source and alert side effects were not fully exercised with backend offline

- Routes: `/sources`, `/alerts`
- Evidence: pages render and controls are available, but backend data and CRUD side effects were not validated because the API backend was offline.
- Suggested owner: UI-R may accept this as residual smoke risk or rerun with a seeded backend.

## Resolved Since Previous QA

- Raw backend error copy: PASS. `/articles`, `/sources`, `/alerts`, and `/archives` now show operator-friendly Chinese fallback copy instead of raw `Internal Server Error`.
- Lint warnings: PASS. `npm run lint` now reports no ESLint warnings or errors.
- UI copy consistency: PASS. Previous all-caps `SOURCES` / `ALERTS` labels were replaced with Chinese operator-facing copy.
- Mobile navigation: PASS. 390px menu button is visible and opens grouped navigation.
- Dark mode readability: PASS. Smoke matrix ran under `html.dark`; page text and error/empty states remained readable.
- Heavy dependency check: PASS. `apps/web/package.json` and lockfile are unchanged.

## Verification

| Check | Result | Summary |
| --- | --- | --- |
| `npm run lint` | PASS | `✔ No ESLint warnings or errors`. |
| `npm run type-check` | PASS | `tsc --noEmit` completed. |
| `npm run build` | PASS | Next.js production build completed; 10 routes generated; no warnings. |
| `npm run test:run` | PASS | Vitest: 1 file, 5 tests passed; Vite CJS deprecation warning only. |
| Heavy dependency check | PASS | `apps/web/package.json` / lockfile unchanged. |
| Backend/API boundary | FAIL | `backend/app/modules/ingest/pipeline.py` modified and `backend/app/modules/ingest/trends_parser.py` untracked in working tree. |
| Route smoke | PASS | All requested routes rendered at 390/768/1280 without framework overlay, raw internal error copy, or horizontal overflow. |
| Mobile navigation | PASS | 390px menu button opened grouped navigation for Workbench, Briefing, Articles, Trends, Archives, Sources, Alerts. |
| Dark mode readability | PASS | Dark mode applied (`html.dark`), body background/text contrast readable. |

## Route Smoke Matrix

| Route | 390px | 768px | 1280px | Notes |
| --- | --- | --- | --- | --- |
| `/` | PASS | PASS | PASS | First screen is `今日情报工作台`, not a marketing page. |
| `/briefing` | PASS | PASS | PASS | 24h/48h/72h controls render; briefing-hours interaction preserved. |
| `/articles` | PASS | PASS | PASS | Filters render; backend offline fallback is friendly Chinese copy. |
| `/articles?source_id=1` | PASS | PASS | PASS | Route renders with source `#1` empty-state copy; no crash. |
| `/sources` | PASS | PASS | PASS | Filters render; source-row actions require backend data for full side-effect verification. |
| `/alerts` | PASS | PASS | PASS | New rule action visible; backend offline fallback is friendly Chinese copy. |
| `/archives` | PASS | PASS | PASS | Stable route; backend offline fallback is friendly Chinese copy. |
| `/trends` | PASS | PASS | PASS | Stable route; segmented day controls render and no overflow. |

## Interaction Evidence

- `/briefing`: briefing-hour controls remain visible and usable.
- `/articles?source_id=1`: route rendered with no overlay; empty-state copy referenced source `#1`.
- `/articles`: filter controls rendered and accepted interaction.
- `/alerts`: `新建规则` button was visible and enabled.
- `/sources`: tier/status filters rendered; source-row operations require backend data for full verification.

## Residual Risk

- Browser smoke was run with backend offline, so CRUD side effects for sources/alerts and populated article/source lists were not fully validated.
- Next dev server logs contain expected proxy `ECONNREFUSED 127.0.0.1:8001` messages from the offline backend.
- Archives/trends render successfully, but data-dependent archive detail and heatmap states still need seeded backend verification.
