#!/usr/bin/env python3
"""M4 / BestBlogs acceptance smoke — run against live API."""

from __future__ import annotations

import argparse
import os
import sys
import time

import httpx

ACCEPTANCE_SLUGS = {
    "bestblogs-featured-zh": {"expect_status": {"success", "failed"}, "min_found": 0},
    "bestblogs-ai-highscore-en": {"expect_status": {"success"}, "min_found": 1},
    "aihot-selected": {"expect_status": {"success", "failed"}, "min_found": 0},
    "aihot-api-selected": {"expect_status": {"success", "skipped", "failed"}, "min_found": 0},
    "osint-bellingcat": {"expect_status": {"success"}, "min_found": 0},
    "hn-search-ai-agents": {"expect_status": {"success"}, "min_found": 1},
}


def _login(client: httpx.Client, base: str) -> None:
    email = os.environ.get("SMOKE_EMAIL", "admin@example.com")
    password = os.environ.get("SMOKE_PASSWORD", "change-me")
    response = client.post(
        f"{base}/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Acceptance ingest smoke")
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()
    base = args.api.rstrip("/")

    with httpx.Client(timeout=30.0) as client:
        try:
            client.get(f"{base}/api/v1/health").raise_for_status()
        except httpx.HTTPError as exc:
            print(f"FAIL health: {exc}", file=sys.stderr)
            return 1

        try:
            _login(client, base)
        except httpx.HTTPError as exc:
            print(
                f"FAIL auth: {exc} — set SMOKE_EMAIL/SMOKE_PASSWORD or INITIAL_ADMIN_*",
                file=sys.stderr,
            )
            return 1

        slug_to_id: dict[str, int] = {}
        page = 1
        while len(slug_to_id) < len(ACCEPTANCE_SLUGS):
            resp = client.get(
                f"{base}/api/v1/sources",
                params={"page": page, "page_size": 100},
            )
            resp.raise_for_status()
            body = resp.json()
            for row in body["data"]:
                if row["slug"] in ACCEPTANCE_SLUGS:
                    slug_to_id[row["slug"]] = row["id"]
            if page >= body.get("total_pages", 1):
                break
            page += 1

        failed = 0
        for slug, rules in ACCEPTANCE_SLUGS.items():
            sid = slug_to_id.get(slug)
            if not sid:
                print(f"FAIL {slug}: source missing (run seed)")
                failed += 1
                continue
            started = time.perf_counter()
            try:
                r = client.post(
                    f"{base}/api/v1/sources/{sid}/ingest",
                    timeout=args.timeout,
                )
                r.raise_for_status()
                data = r.json()
            except httpx.HTTPError as exc:
                print(f"FAIL {slug}: HTTP {exc}")
                failed += 1
                continue

            status = data.get("status", "")
            found = int(data.get("items_found") or 0)
            created = int(data.get("items_created") or 0)
            ms = int((time.perf_counter() - started) * 1000)
            err = (data.get("error_message") or "")[:100]

            ok = status in rules["expect_status"] and found >= rules["min_found"]
            if status == "skipped" and "aihot" in slug:
                # aihot-api may skip if upstream 403 — warn not fail
                if "aihot" in err.lower() or "only supports" in err.lower():
                    ok = status != "skipped" or "aihot-api" not in slug
            if status == "skipped" and slug == "aihot-api-selected":
                ok = False

            label = "PASS" if ok else "FAIL"
            print(
                f"{label} {slug}: status={status} found={found} created={created} {ms}ms"
                + (f" err={err}" if err else "")
            )
            if not ok:
                failed += 1

        stats = client.get(f"{base}/api/v1/stats/overview").json()["data"]
        briefing = client.get(
            f"{base}/api/v1/briefings/daily",
            params={"hours": 24, "limit": 5},
            timeout=60.0,
        )
        briefing.raise_for_status()
        bdata = briefing.json()["data"]
        item_count = bdata["meta"]["item_count"]

        print(
            f"\nStats: articles={stats['articles_total']} reports={stats['reports_total']} "
            f"sources_enabled={stats['sources_enabled']}"
        )
        print(f"Briefing 24h: {item_count} items (ai_mode={bdata['meta']['ai_mode']})")

        archives = client.get(f"{base}/api/v1/archives", params={"page_size": 5})
        archives.raise_for_status()
        archive_rows = archives.json().get("data") or []
        trends = client.get(
            f"{base}/api/v1/archives/trends/category-heat",
            params={"days": 7},
        )
        trends.raise_for_status()
        trend_data = trends.json().get("data") or {}
        tz = trend_data.get("timezone", "")
        cat_count = len(trend_data.get("categories") or [])

        if tz != "Asia/Shanghai":
            print(f"WARN archives timezone={tz} (expected Asia/Shanghai)")
        print(f"Archives: {len(archive_rows)} recent row(s) · trends categories={cat_count}")
        if not archive_rows:
            print("WARN no archive rows yet — run archive_daily_snapshot or backfill-archives.py")

        if failed:
            print(f"\nAcceptance: {failed} check(s) failed", file=sys.stderr)
            return 1
        print("\nAcceptance: ALL PASS")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
