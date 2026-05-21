#!/usr/bin/env python3
"""Patch API sources missing URLs from seeds/all-sources.json (by slug)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "seeds" / "all-sources.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill empty source URLs from seed JSON")
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--seed", default=str(DEFAULT_SEED))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    seed_by_slug = {
        row["slug"]: row
        for row in json.loads(Path(args.seed).read_text(encoding="utf-8"))
        if row.get("url")
    }
    base = args.api.rstrip("/")
    patched = skipped = 0

    with httpx.Client(timeout=60.0) as client:
        page = 1
        while True:
            resp = client.get(f"{base}/api/v1/sources", params={"page": page, "page_size": 100})
            resp.raise_for_status()
            body = resp.json()
            for src in body["data"]:
                if src.get("url"):
                    skipped += 1
                    continue
                seed = seed_by_slug.get(src["slug"])
                if not seed or not seed.get("url"):
                    continue
                payload = {
                    "url": seed["url"],
                    "source_type": seed.get("type") or seed.get("source_type") or "rss",
                }
                if args.dry_run:
                    print(f"would patch #{src['id']} {src['slug']}: {payload['url'][:60]}")
                else:
                    r = client.patch(f"{base}/api/v1/sources/{src['id']}", json=payload)
                    r.raise_for_status()
                    print(f"patched #{src['id']} {src['slug']}")
                patched += 1
            if page >= body.get("total_pages", 1):
                break
            page += 1

    print(f"Done: patched={patched}, already_had_url={skipped}")


if __name__ == "__main__":
    main()
