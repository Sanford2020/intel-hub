# Debug Workflow

Use this workflow for bugs, failed tests, broken local startup, API errors, UI regressions, worker failures, and deployment issues.

## Flow

```text
Reproduce
  -> isolate scope
  -> smallest fix
  -> verify
  -> record cause
```

## Step 1: Reproduce

- Record exact command, URL, input, or user action.
- Capture relevant logs or screenshots.
- Confirm whether the issue is frontend, backend, worker, database, Docker, or environment.

## Step 2: Locate Scope

- Identify the smallest likely module.
- Read related tests and docs.
- Check recent changes only if git history is available.
- Avoid broad rewrites.

## Step 3: Minimal Change

- Fix the smallest confirmed cause.
- Do not change unrelated formatting or architecture.
- If the problem is structural, record it in `REVIEW.md` and create a task.

## Step 4: Test Verification

Run the narrowest relevant check, then broaden if needed:

```powershell
python -m pytest path/to/test.py -q
npm run type-check
npm run build
docker compose config
```

## Step 5: Record Cause

Update the task or `REVIEW.md` with:

- Symptom.
- Root cause.
- Fix.
- Verification.
- Follow-up risk.

## Debug Constraints

- Do not silence errors without explaining why.
- Do not remove tests to pass CI.
- Do not commit local secrets or generated logs.
- Do not assume production behavior from mock mode.
