"""Poll Intel Hub health and overview stats for ops observation windows."""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


def fetch_json(url: str, timeout: float) -> tuple[bool, dict[str, Any] | str]:
    try:
        with urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return True, payload
    except (OSError, URLError, json.JSONDecodeError) as exc:
        return False, str(exc)


def unwrap_data(payload: dict[str, Any] | str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data")
    return data if isinstance(data, dict) else payload


def build_row(api: str, timeout: float) -> dict[str, Any]:
    observed_at = datetime.now(timezone.utc).isoformat()
    health_ok, health_payload = fetch_json(f"{api}/api/v1/health", timeout)
    stats_ok, stats_payload = fetch_json(f"{api}/api/v1/stats/overview", timeout)
    stats = unwrap_data(stats_payload)

    return {
        "observed_at_utc": observed_at,
        "health_ok": health_ok,
        "health_status": unwrap_data(health_payload).get("status", ""),
        "stats_ok": stats_ok,
        "sources_total": stats.get("sources_total", ""),
        "sources_enabled": stats.get("sources_enabled", ""),
        "articles_total": stats.get("articles_total", ""),
        "reports_total": stats.get("reports_total", ""),
        "alert_rules_total": stats.get("alert_rules_total", ""),
        "alert_rules_enabled": stats.get("alert_rules_enabled", ""),
        "alert_events_total": stats.get("alert_events_total", ""),
        "error": "" if health_ok and stats_ok else f"health={health_payload}; stats={stats_payload}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:8001")
    parser.add_argument("--interval", type=float, default=60.0)
    parser.add_argument("--iterations", type=int, default=0, help="0 means run forever")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--out", default="docs/operations/worker-observation-samples.csv")
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
        "error",
    ]
    write_header = not out_path.exists() or out_path.stat().st_size == 0

    count = 0
    with out_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        while args.iterations == 0 or count < args.iterations:
            row = build_row(args.api.rstrip("/"), args.timeout)
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
