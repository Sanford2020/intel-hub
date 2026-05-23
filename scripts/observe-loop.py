"""Poll Intel Hub health, overview stats, and Redis queue depth for ops observation."""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

try:
    import redis
except ImportError:  # pragma: no cover - optional at runtime
    redis = None  # type: ignore[assignment]


def login(client: httpx.Client, base: str) -> None:
    email = os.environ.get("SMOKE_EMAIL", "admin@example.com")
    password = os.environ.get("SMOKE_PASSWORD", "change-me")
    response = client.post(
        f"{base}/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"


def queue_lengths(redis_url: str | None) -> dict[str, int | str]:
    if not redis_url or redis is None:
        return {"default_queue": "", "ingest_queue": ""}
    try:
        client = redis.Redis.from_url(redis_url, decode_responses=True)
        return {
            "default_queue": int(client.llen("default") or 0),
            "ingest_queue": int(client.llen("ingest") or 0),
        }
    except Exception as exc:  # noqa: BLE001
        return {"default_queue": f"err:{exc}", "ingest_queue": f"err:{exc}"}


def unwrap_data(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    return data if isinstance(data, dict) else payload


def build_row(
    client: httpx.Client,
    base: str,
    redis_url: str | None,
) -> dict[str, Any]:
    observed_at = datetime.now(timezone.utc).isoformat()
    row: dict[str, Any] = {
        "observed_at_utc": observed_at,
        "health_ok": False,
        "health_status": "",
        "stats_ok": False,
        "sources_total": "",
        "sources_enabled": "",
        "articles_total": "",
        "reports_total": "",
        "alert_rules_total": "",
        "alert_rules_enabled": "",
        "alert_events_total": "",
        "default_queue": "",
        "ingest_queue": "",
        "error": "",
    }

    try:
        health = client.get(f"{base}/api/v1/health")
        row["health_ok"] = health.status_code == 200
        if row["health_ok"]:
            row["health_status"] = unwrap_data(health.json()).get("status", "")
    except httpx.HTTPError as exc:
        row["error"] = f"health:{exc}"

    try:
        stats = client.get(f"{base}/api/v1/stats/overview")
        row["stats_ok"] = stats.status_code == 200
        if row["stats_ok"]:
            data = unwrap_data(stats.json())
            row["sources_total"] = data.get("sources_total", "")
            row["sources_enabled"] = data.get("sources_enabled", "")
            row["articles_total"] = data.get("articles_total", "")
            row["reports_total"] = data.get("reports_total", "")
            row["alert_rules_total"] = data.get("alert_rules_total", "")
            row["alert_rules_enabled"] = data.get("alert_rules_enabled", "")
            row["alert_events_total"] = data.get("alert_events_total", "")
    except httpx.HTTPError as exc:
        row["error"] = (row["error"] + f"; stats:{exc}").strip("; ")

    queues = queue_lengths(redis_url)
    row["default_queue"] = queues["default_queue"]
    row["ingest_queue"] = queues["ingest_queue"]
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:8001")
    parser.add_argument("--interval", type=float, default=60.0)
    parser.add_argument("--iterations", type=int, default=0, help="0 means run forever")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument(
        "--redis-url",
        default=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    )
    parser.add_argument(
        "--out",
        default="docs/operations/worker-observation-samples.csv",
    )
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "observed_at_utc",
        "health_ok",
        "health_status",
        "stats_ok",
        "sources_total",
        "sources_enabled",
        "articles_total",
        "reports_total",
        "alert_rules_total",
        "alert_rules_enabled",
        "alert_events_total",
        "default_queue",
        "ingest_queue",
        "error",
    ]
    write_header = not out_path.exists() or out_path.stat().st_size == 0

    base = args.api.rstrip("/")
    count = 0
    with httpx.Client(timeout=args.timeout) as client, out_path.open(
        "a", newline="", encoding="utf-8"
    ) as handle:
        login(client, base)
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        while args.iterations == 0 or count < args.iterations:
            row = build_row(client, base, args.redis_url)
            writer.writerow(row)
            handle.flush()
            print(json.dumps(row, ensure_ascii=False))
            count += 1
            if args.iterations != 0 and count >= args.iterations:
                break
            time.sleep(args.interval)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
