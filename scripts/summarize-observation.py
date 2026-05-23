#!/usr/bin/env python3
"""Summarize worker observation CSV samples for OPS-03 reports."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def to_int(value: str | int | float) -> int | None:
    if value == "" or value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        return {"error": "no rows"}

    first, last = rows[0], rows[-1]
    stats_rows = [r for r in rows if r.get("stats_ok") == "True"]
    health_failures = sum(1 for r in rows if r.get("health_ok") != "True")
    stats_failures = sum(1 for r in rows if r.get("stats_ok") != "True")

    def delta(field: str) -> int | None:
        start = to_int(first.get(field, ""))
        end = to_int(last.get(field, ""))
        if start is None or end is None:
            return None
        return end - start

    default_queues = [to_int(r.get("default_queue", "")) for r in rows]
    default_queues = [q for q in default_queues if q is not None]
    ingest_queues = [to_int(r.get("ingest_queue", "")) for r in rows]
    ingest_queues = [q for q in ingest_queues if q is not None]

    return {
        "samples": len(rows),
        "window_start_utc": first.get("observed_at_utc"),
        "window_end_utc": last.get("observed_at_utc"),
        "health_failures": health_failures,
        "stats_failures": stats_failures,
        "start": {
            "sources_total": first.get("sources_total"),
            "sources_enabled": first.get("sources_enabled"),
            "articles_total": first.get("articles_total"),
            "reports_total": first.get("reports_total"),
            "alert_events_total": first.get("alert_events_total"),
            "default_queue": first.get("default_queue"),
            "ingest_queue": first.get("ingest_queue"),
        },
        "end": {
            "sources_total": last.get("sources_total"),
            "sources_enabled": last.get("sources_enabled"),
            "articles_total": last.get("articles_total"),
            "reports_total": last.get("reports_total"),
            "alert_events_total": last.get("alert_events_total"),
            "default_queue": last.get("default_queue"),
            "ingest_queue": last.get("ingest_queue"),
        },
        "delta": {
            "articles_total": delta("articles_total"),
            "reports_total": delta("reports_total"),
            "alert_events_total": delta("alert_events_total"),
        },
        "queue": {
            "default_min": min(default_queues) if default_queues else None,
            "default_max": max(default_queues) if default_queues else None,
            "default_last": default_queues[-1] if default_queues else None,
            "ingest_max": max(ingest_queues) if ingest_queues else None,
        },
        "stats_ok_samples": len(stats_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="?", default="docs/operations/worker-observation-samples.csv")
    args = parser.parse_args()
    path = Path(args.csv)
    if not path.exists():
        print(json.dumps({"error": f"missing {path}"}))
        return 1
    print(json.dumps(summarize(load_rows(path)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
