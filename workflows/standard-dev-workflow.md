# Standard Development Workflow

Use this workflow for planned features, UI changes, API changes, worker changes, and documentation changes.

## Flow

```text
Cursor planning
  -> Windsurf implementation
  -> Codex test/fix
  -> Cursor review
  -> update TASKS/DECISIONS/REVIEW
```

## Step 1: Cursor Planning

- Read `AGENTS.md`, `ARCHITECTURE.md`, `TASKS.md`, and relevant docs.
- Clarify goal, constraints, affected modules, and acceptance criteria.
- Create or update the task in `TASKS.md`.
- Decide if an ADR is needed in `DECISIONS.md`.
- Produce prompts for Windsurf and Codex.

## Step 2: Windsurf Implementation

- Implement only the assigned task.
- Avoid unrelated refactors.
- Keep frontend/backend contracts aligned.
- Update docs/tests/types if required.
- Return changed files and expected tests.

## Step 3: Codex Test And Fix

- Run targeted tests first.
- Run broader checks if shared modules or contracts changed.
- Fix the smallest confirmed issue.
- Report results and remaining risks.

## Step 4: Cursor Review

- Check feature fit against PRD/task.
- Check architecture consistency.
- Check API/docs/test updates.
- Decide whether task moves to `DONE` or back to `TODO`.

## Step 5: Record Keeping

- Move task status in `TASKS.md`.
- Add ADR to `DECISIONS.md` when architecture changed.
- Add unresolved risks to `REVIEW.md`.
- Update `docs/api.md`, `docs/deployment.md`, or `docs/prd.md` when relevant.

## Done Criteria

- Acceptance criteria met.
- Tests pass or blockers documented.
- Docs updated.
- Review findings resolved or converted to tasks.
