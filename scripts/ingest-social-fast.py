#!/usr/bin/env python3
"""Fast ingest for social/aggregator sources (AI HOT, BestBlogs, HN, Reddit async)."""

from __future__ import annotations

import argparse
import sys
import time

import httpx

FAST_SLUGS = [
    "aihot-selected",
    "aihot-all",
    "aihot-api-selected",
    "aihot-api-all",
    "bestblogs-featured-zh",
    "bestblogs-ai-highscore-zh",
    "bestblogs-twitter-zh",
    "bestblogs-daily-brief-zh",
    "hn-search-cybersecurity",
    "hn-search-geopolitics",
    "hn-search-ai-agents",
    "reddit-r-geopolitics",
    "reddit-r-cybersecurity",
    "reddit-r-osint",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest AI HOT + BestBlogs + HN + Reddit (async)")
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base = args.api.rstrip("/")

    with httpx.Client(timeout=30.0) as client:
        health = client.get(f"{base}/api/v1/health")
        health.raise_for_status()

        slug_to_id: dict[str, int] = {}
        page = 1
        while len(slug_to_id) < len(FAST_SLUGS):
            resp = client.get(
                f"{base}/api/v1/sources",
                params={"page": page, "page_size": 100},
            )
            resp.raise_for_status()
            body = resp.json()
            for row in body["data"]:
                if row["slug"] in FAST_SLUGS:
                    slug_to_id[row["slug"]] = row["id"]
            if page >= body.get("total_pages", 1):
                break
            page += 1

        missing = [s for s in FAST_SLUGS if s not in slug_to_id]
        if missing:
            print(f"Missing sources (run seed first): {', '.join(missing)}", file=sys.stderr)

        for slug in FAST_SLUGS:
            sid = slug_to_id.get(slug)
            if not sid:
                continue
            r = client.post(
                f"{base}/api/v1/sources/{sid}/ingest",
                params={"async": "true"},
                timeout=15.0,
            )
            r.raise_for_status()
            task = r.json().get("task_id", "?")[:8]
            print(f"QUE #{sid} {slug} task={task}")
            time.sleep(0.3)

        stats = client.get(f"{base}/api/v1/stats/overview").json()["data"]
        print(
            f"\nQueued {len(slug_to_id)} sources. Worker must be running. "
            f"Articles now: {stats['articles_total']}"
        )


if __name__ == "__main__":
    main()
