# Review Workflow

Use this workflow before marking tasks done, before release, and after large AI-generated changes.

## Review Order

1. Functional fit.
2. Architecture consistency.
3. API and data contract consistency.
4. Test coverage.
5. Security risks.
6. Performance risks.
7. Documentation updates.
8. AI collaboration compliance.

## Functional Fit

- Does the change satisfy the task in `TASKS.md`?
- Does it preserve existing user workflows?
- Are loading, empty, error, and success states covered where relevant?

## Architecture Consistency

- Does the change follow `ARCHITECTURE.md`?
- Does it keep route handlers thin and service logic in modules?
- Does frontend code follow existing Next.js patterns?
- Are worker tasks registered and named consistently?

## API And Data Contracts

- If endpoints changed, is `docs/api.md` updated?
- Are frontend types updated?
- Are response shapes consistent?
- Are pagination/filter parameters documented?

## Test Coverage

- Are relevant backend tests present?
- Are frontend type-check/build checks passing?
- Are worker or integration paths verified?
- Are skipped or missing tests documented?

## Security Review

- No secrets in committed files.
- No unsafe CORS changes.
- No auth bypass for commercial endpoints.
- No unvalidated external input reaching sensitive operations.

## Performance Review

- Queries should avoid obvious N+1 patterns.
- Lists should use pagination.
- Frontend should avoid unnecessary blocking work.
- Workers should avoid unbounded batches.

## Documentation Review

- Product behavior changes update `docs/prd.md`.
- API changes update `docs/api.md`.
- Deployment/runtime changes update `docs/deployment.md`.
- Architecture decisions update `DECISIONS.md`.
- Known risks update `REVIEW.md`.

## Review Output

```markdown
Findings:
- P0/P1/P2/P3 finding

Passed Checks:
- check

Required Follow-ups:
- task

Decision:
- Approved | Changes requested | Blocked
```
