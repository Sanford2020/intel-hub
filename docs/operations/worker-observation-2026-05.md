# Worker / Beat Observation — 2026-05-22

Verdict: BLOCK for OPS-03 24h closure; PASS for short-run task discovery and Beat dispatch evidence.

## Scope

- Task: `TASK-20260521-OPS-03`
- Host: local Windows development machine
- Observation window: short run, about 22:04–22:17 Asia/Shanghai on 2026-05-22
- This is not a 24h reliability observation.
- Backend URL: `http://127.0.0.1:8001`
- Broker/result backend: Redis on `localhost:6379`
- Database: PostgreSQL on `localhost:5432`

## Service State

| Service | Result | Evidence |
| --- | --- | --- |
| PostgreSQL | PASS | `docker compose ps`: `intel-hub-db-1` healthy. |
| Redis | PASS | `docker compose ps`: `intel-hub-redis-1` healthy; `redis-cli PING` returned `PONG`. |
| Backend | PASS | `/api/v1/health` returned `healthy`. |
| Celery worker | PASS with risk | Worker eventually consumed queued tasks, but startup/inspect was slow and remote control timed out. |
| Celery beat | PASS with risk | Beat sent due dispatch tasks; first exact run encountered a corrupt local `celerybeat-schedule` file and removed it. |

## Task Registration

Initial worker banner before the import fix did not list `workers.tasks.archives.snapshot.archive_daily_snapshot`.

`workers/tasks/archives/__init__.py` only contained a package docstring, so Celery autodiscovery imported the package without importing `snapshot.py`. This was fixed as a trivial registration import.

After the fix, local Celery app discovery and the worker banner listed:

- `workers.tasks.alerts.match.evaluate_alerts_for_article`
- `workers.tasks.analyze.dispatch.dispatch_unanalyzed_articles`
- `workers.tasks.analyze.summarize.analyze_article`
- `workers.tasks.archives.snapshot.archive_daily_snapshot`
- `workers.tasks.briefings.generate.generate_daily_briefing`
- `workers.tasks.ingest.fetch_rss.dispatch_due_rss_sources`
- `workers.tasks.ingest.fetch_rss.fetch_rss_for_source`

## Beat Schedule

`workers.celery_app` contains:

| Beat entry | Task | Schedule |
| --- | --- | --- |
| `dispatch-due-rss-sources` | `workers.tasks.ingest.fetch_rss.dispatch_due_rss_sources` | every 5 minutes |
| `dispatch-unanalyzed-articles` | `workers.tasks.analyze.dispatch.dispatch_unanalyzed_articles` | every 10 minutes |
| `generate-daily-briefing` | `workers.tasks.briefings.generate.generate_daily_briefing` | 06:00 UTC daily |
| `archive-daily-snapshot` | `workers.tasks.archives.snapshot.archive_daily_snapshot` | 06:15 UTC daily |

Short-run Beat evidence:

- 22:10:21: sent `dispatch-unanalyzed-articles`.
- 22:11:03: sent `dispatch-due-rss-sources`.
- 22:15:21: sent `dispatch-due-rss-sources`.

Daily briefing and archive tasks were verified in the Beat schedule and worker registration, but were not naturally executed in this short observation window.

## Runtime Evidence

Stats samples:

| Time UTC | Sources total/enabled | Articles | Reports | Alert events |
| --- | --- | --- | --- | --- |
| 14:14:51 | 567 / 276 | 4215 | 3954 | 2894 |
| 14:16:12 | 567 / 276 | 4310 | 4069 | 2969 |
| 14:17:29 | 567 / 276 | 4526 | 4069 | 2969 |

Worker logs showed:

- `analyze_article` tasks received and succeeded in mock mode.
- At least one alert fired for keyword `AI` under rule `Geopolitics Watch`.
- `fetch_rss_for_source` tasks were received.
- RSS failures included Reuters `404 Not Found`, SSL EOF errors, and AP invalid XML.

Redis queue state after stopping the short run:

- `default` queue length: 623
- `ingest` queue length: 0

The queue grew during the short run because Beat dispatched due sources and the single local Windows worker could not drain them quickly.

## Command Results

| Command | Result | Summary |
| --- | --- | --- |
| `celery -A workers.celery_app inspect registered` | FAIL | Timed out waiting for worker remote-control response. Worker banner/local app registry provided task-list evidence instead. |
| `celery -A workers.celery_app inspect scheduled` | FAIL | Timed out waiting for worker remote-control response. No ETA tasks were confirmed by inspect. |
| `celery -A workers.celery_app beat --loglevel=info` | FAIL / observed separately | Foreground validation timed out in the shell; background Beat with a temp schedule file started and sent due tasks. First run also removed a corrupt local schedule file. |
| `pytest -q` | PASS | 80 passed in 14.42s. |
| `powershell -ExecutionPolicy Bypass -File scripts/validate_project.ps1 -Quick -SkipDocker` | PASS | Backend pytest 80 passed; frontend type-check passed; Docker and frontend build skipped by flags. |

## Risks

- No 24h observation was performed; OPS-03 cannot close the original 24h requirement.
- Celery remote control is unreliable in this local Windows run: `inspect registered` and `inspect scheduled` timed out.
- Beat can enqueue faster than the local single worker drains when many sources are due; the `default` queue ended with 623 messages.
- Local `celerybeat-schedule` can become corrupted; using a clean schedule path recovered the short run.
- AI ran in mock mode because `OPENAI_API_KEY` is empty.
- Several RSS sources still fail at runtime; OPS-01 reduced known bad enabled seeds, but database state still includes failing due sources.

## Conclusion

Commercial daily operations are not yet signed off by OPS-03. The task graph and Beat schedule are now registered correctly, and a short run proved analyze, ingest, and alert execution paths can run. A supervised 24h run is still required on a stable host with queue-depth sampling, Beat logs, worker logs, and final source/article/report/alert deltas.
