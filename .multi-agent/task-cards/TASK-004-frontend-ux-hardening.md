# TASK-004: Frontend UX Hardening

## Task Info

- Type: frontend / QA
- Priority: P1
- Status: done
- Owner: Frontend Agent

## Goal

Make the dashboard clearer when backend, data, or AI analysis is unavailable, and ensure all core routes remain easy to scan on desktop and mobile.

## Allowed Changes

| Path | Purpose |
| --- | --- |
| `apps/web/src/app/**` | Pages and route-level states |
| `apps/web/src/components/**` | Shared UI/layout components |
| `apps/web/src/lib/**` | API error handling helpers |
| `apps/web/src/types/**` | Frontend types |

## Acceptance Criteria

- Home, sources, articles, article detail, and alerts show useful empty/error/loading states.
- Backend offline state is visible without breaking navigation.
- `npm run type-check` passes.
- `npm run build` passes or any failure is documented with cause.

## Verification

```powershell
cd apps\web
npm run type-check
npm run build
```

## Completion Notes

- Reframed the dashboard as a commercial intelligence operations surface.
- Hardened navigation, homepage status, source/article/alert screens, empty states, and mobile layout.
- Verified with `npm run type-check`, `npm run build`, route scan, and mock-mode screenshots.
