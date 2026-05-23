# M5.5 UI-F2 QA Recheck — 2026-05-22 (superseded)

Verdict: REQUEST_CHANGES — see F2-FIX recheck below.

---

# M5.5 UI-F2-FIX QA Recheck — 2026-05-23

Verdict: **APPROVE**

## Scope

- Fixes: AppNav `body overflow:hidden` on mobile drawer; `min-w-0` / `app-shell` overflow guards; `/trends` `dedupePointsByDate()`
- Auth integration: `/login`, middleware (pages only; `/api/*` excluded for proxy)
- App URL: `http://127.0.0.1:3000` · Backend: `http://127.0.0.1:8001`
- Viewport: **390px** (CDP mobile emulation)

## Blocker resolution

| ID | Prior issue | Recheck |
| --- | --- | --- |
| UI-F2-01 | 390px horizontal overflow on `/articles` and `/` after drawer | **PASS** — `scrollWidth=390`, `clientWidth=390`; drawer open `bodyOverflow=hidden`, no page overflow |
| UI-F2-02 | Duplicate React keys on `/trends` | **PASS** — dedupe helper in `trends/page.tsx`; page loads without key collision |

## Verification

| Check | Result |
| --- | --- |
| `npm run lint` | PASS |
| `npm run type-check` | PASS |
| `npm run build` | PASS |
| Login flow | PASS — `/login` → home with `ih_auth=1` cookie |
| 390px `/articles` | PASS — no horizontal overflow |
| 390px `/` + drawer | PASS — no horizontal overflow |

---

# M5.5 UI-F2 QA Recheck — 2026-05-22 (original)

Verdict: REQUEST_CHANGES

## Scope

- Plan: `docs/plans/M5.5-frontend-intelligence-workbench-redesign.md`
- Task: `TASK-20260522-UI-QA`
- App URL: `http://127.0.0.1:3000`
- Backend URL: `http://127.0.0.1:8001`
- Browser: Codex in-app Browser
- Viewports: 390px, 768px, 1280px
- Detail smoke data: `/articles/295`, `/archives/2026-05-21`

## Summary

UI-F2 is close, but not ready for APPROVE. The main redesign goals are now met: `/` is an intelligence workbench, briefing and trends share the new shell/controls, raw `Internal Server Error` no longer appears, mobile navigation opens, dark mode is readable, and core interactions still work.

Remaining blockers for UI approval are mobile layout overflow and a React key warning in trends. These are frontend-only findings and should be fixed by Windsurf UI-F2 before UI-R.

## Findings

### P1 — 390px mobile layout has horizontal overflow

- Files: `apps/web/src/app/articles/page.tsx`, `apps/web/src/components/layout/AppNav.tsx`, likely dashboard card sizing in `apps/web/src/app/page.tsx`
- Evidence:
  - `/articles` at 390px: `documentElement.scrollWidth=385`, `clientWidth=375`; filter controls with class `field` render from `left=32.67` to `right=384.67`.
  - After opening the 390px mobile drawer on `/`: `scrollWidth=585`, `clientWidth=375`; dashboard `surface` cards extend to `right=584.7`.
- Why it matters: The M5.5 plan explicitly requires mobile navigation and mobile pages not to break layout. Horizontal page scrolling is visible polish debt for commercial delivery.
- Suggested owner: Windsurf UI-F2.

### P2 — `/trends` emits duplicate React key warnings

- File: `apps/web/src/app/trends/page.tsx`
- Evidence: Browser console repeatedly logs `Encountered two children with the same key, 2026-05-20`; stack points to `TrendsPage` around repeated date keys in trend cards/table.
- Why it matters: `npm run lint` passes, but runtime key collisions can duplicate/omit cells and make trend rendering unstable with archive data.
- Suggested owner: Windsurf UI-F2.

### Residual — Non-UI worker change exists in working tree

- File: `workers/tasks/archives/__init__.py`
- Evidence: `git diff --name-status -- backend workers services ...` reports `M workers/tasks/archives/__init__.py`.
- Why it matters: This is not an API/backend business change from UI-F2; it is the prior OPS-03 trivial Celery registration fix. UI-R should account for it separately so UI review is not confused with ops scope.

## Verification

| Check | Result | Summary |
| --- | --- | --- |
| `npm run lint` | PASS | `✔ No ESLint warnings or errors`. |
| `npm run type-check` | PASS | `tsc --noEmit` completed. |
| `npm run build` | PASS | Next.js production build completed; 10 routes generated; no warnings. |
| `npm run test:run` | PASS | Vitest: 1 file, 5 tests passed; Vite CJS deprecation warning only. |
| Heavy dependency check | PASS | No `apps/web/package.json` / lockfile diff observed. |
| Backend/API boundary | PASS for UI-F2 | No backend API/client/type/package diff from UI-F2; existing worker diff belongs to OPS-03. |
| Route smoke | PASS with findings | All requested routes rendered without framework overlay or raw internal error. |
| Mobile navigation | PASS with overflow finding | 390px menu button opened grouped navigation and all core links were visible; page overflowed horizontally after opening. |
| Dark mode readability | PASS | Light/dark text/background pairs were readable in smoke. |

## Route Smoke Matrix

| Route | 390px | 768px | 1280px | Notes |
| --- | --- | --- | --- | --- |
| `/` | PASS with finding | PASS | PASS | First screen is `今日情报工作台`; drawer opens at 390px but page overflows after opening. |
| `/briefing` | PASS | PASS | PASS | New visual shell and 24h/48h/72h controls present. |
| `/articles` | FAIL | PASS | PASS | 390px horizontal overflow in filter controls. |
| `/articles?source_id=1` | PASS | PASS | PASS | Query behavior preserved and no raw error. |
| `/articles/295` | PASS | PASS | PASS | Detail page rendered article title, source/time, original link, AI summary, score/tags. |
| `/sources` | PASS | PASS | PASS | Operator copy localized; no raw error. |
| `/alerts` | PASS | PASS | PASS | New rule action visible; no raw error. |
| `/archives` | PASS | PASS | PASS | New visual shell; no raw error. |
| `/archives/2026-05-21` | PASS | PASS | PASS | Detail page rendered archive title, heat categories, briefing overview/items. |
| `/trends` | PASS with finding | PASS with finding | PASS with finding | New visual shell and 7/14/30 controls present; duplicate key console warning. |

## Interaction Evidence

- `/briefing`: clicked `48h`; page reflected the 48h state.
- `/articles?source_id=1`: route stayed at `/articles?source_id=1`, no raw error, source-specific results rendered.
- `/trends`: clicked `14 天`; control remained available and no raw error appeared.
- `/alerts`: `新建规则` action visible.
- Mobile nav: `button[aria-label="打开菜单"]` count was 1 at 390px; drawer opened and showed Workbench, Briefing, Articles, Trends, Archives, Sources, Alerts.

## Residual Risk

- Smoke used a live local backend with mock AI mode and a data-heavy database. Behavior may differ in an empty seeded environment, though empty/loading/error states were visible.
- Source/alert CRUD side effects were not submitted; QA only verified controls remained present and pages did not crash.
