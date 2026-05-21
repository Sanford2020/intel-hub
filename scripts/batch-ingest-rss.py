#!/usr/bin/env python3
"""Trigger ingest for enabled RSS and X sources that have a URL."""

from __future__ import annotations

import argparse
import sys
import time

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch ingest enabled RSS/X sources")
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--limit", type=int, default=20, help="Max sources to ingest")
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between requests")
    parser.add_argument("--timeout", type=float, default=25.0, help="Per-source ingest timeout (seconds)")
    parser.add_argument(
        "--async",
        dest="async_mode",
        action="store_true",
        help="Queue Celery ingest tasks (non-blocking, recommended for batch)",
    )
    args = parser.parse_args()
    base = args.api.rstrip("/")

    ingest_timeout = httpx.Timeout(args.timeout)
    with httpx.Client(timeout=120.0) as client:
        page = 1
        candidates: list[dict] = []
        while len(candidates) < args.limit:
            resp = client.get(
                f"{base}/api/v1/sources",
                params={"page": page, "page_size": 100, "enabled": True},
            )
            resp.raise_for_status()
            body = resp.json()
            for row in body["data"]:
                st = row.get("source_type")
                if st in ("rss", "x", "reddit", "hn", "polymarket", "aihot", "apify") and row.get("url"):
                    candidates.append(row)
                    if len(candidates) >= args.limit:
                        break
            if page >= body.get("total_pages", 1):
                break
            page += 1

        if not candidates:
            print("No enabled RSS/X sources with URL found.", file=sys.stderr)
            raise SystemExit(1)

        print(f"Ingesting {len(candidates)} RSS/X sources (async={args.async_mode})...")
        ok = failed = created = 0
        for src in candidates:
            sid = src["id"]
            name = src["name"]
            try:
                if args.async_mode:
                    r = client.post(f"{base}/api/v1/sources/{sid}/ingest", params={"async": "true"}, timeout=10.0)
                else:
                    r = client.post(f"{base}/api/v1/sources/{sid}/ingest", timeout=ingest_timeout)
                r.raise_for_status()
                result = r.json()
                status = result.get("status", "unknown")
                if args.async_mode:
                    if status == "queued":
                        ok += 1
                        print(f"  QUE #{sid} {name}: task={result.get('task_id', '?')[:8]}")
                    else:
                        failed += 1
                        print(f"  FAIL #{sid} {name}: status={status}", file=sys.stderr)
                    continue
                items = result.get("items_created", 0)
                if status == "failed":
                    failed += 1
                    err = result.get("error_message", "unknown")[:80]
                    print(f"  FAIL #{sid} {name}: {err}", file=sys.stderr)
                else:
                    created += items
                    ok += 1
                    print(f"  OK  #{sid} {name}: +{items} articles")
            except httpx.HTTPError as exc:
                failed += 1
                print(f"  FAIL #{sid} {name}: {exc}", file=sys.stderr)
            time.sleep(args.delay)

        stats = client.get(f"{base}/api/v1/stats/overview").json()["data"]
        if args.async_mode:
            print(
                f"\nDone: queued={ok}, failed={failed}. "
                f"Worker will ingest in background. "
                f"Totals now: articles={stats['articles_total']}, reports={stats['reports_total']}"
            )
        else:
            print(
                f"\nDone: {ok} ok, {failed} failed, +{created} new articles this run. "
                f"Totals: articles={stats['articles_total']}, reports={stats['reports_total']}"
            )


if __name__ == "__main__":
    main()
