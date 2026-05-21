#!/usr/bin/env python3
"""
Sync seeds/all-sources.json to a Notion database.

Requires:
  NOTION_API_KEY   — integration token (https://www.notion.so/my-integrations)
  NOTION_PARENT_PAGE_ID — page where the database will be created (if NOTION_DATABASE_ID unset)
  NOTION_DATABASE_ID — optional existing database ID (skip create)

Usage:
  pip install notion-client
  python scripts/parse-data-sources.py
  python scripts/sync-sources-to-notion.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
except ImportError:
    print("Install: pip install notion-client")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "seeds" / "all-sources.json"

DB_TITLE = "Intel Hub — 情报数据源"
DB_PROPERTIES = {
    "Slug": {"rich_text": {}},
    "Category": {"select": {"options": [{"name": c} for c in [
        "wire", "regional", "official", "financial", "geopolitical", "cyber",
        "social", "research", "vertical", "aggregator", "maritime",
        "compliance", "humanitarian", "china", "thinktank", "other",
    ]]}},
    "Category Label": {"rich_text": {}},
    "Subcategory": {"rich_text": {}},
    "Type": {"select": {"options": [{"name": t} for t in [
        "rss", "rest_api", "gdelt", "acled", "telegram", "scraper", "webhook", "unknown",
    ]]}},
    "URL": {"url": {}},
    "Language": {"rich_text": {}},
    "Region": {"rich_text": {}},
    "Tier": {"select": {"options": [{"name": "0"}, {"name": "1"}, {"name": "2"}]}},
    "Enabled": {"checkbox": {}},
    "API Key Env": {"rich_text": {}},
    "License Notes": {"rich_text": {}},
    "Section": {"rich_text": {}},
    "Source File": {"rich_text": {}},
}


def rt(text: str) -> dict:
    if not text:
        return {"rich_text": []}
    return {"rich_text": [{"type": "text", "text": {"content": str(text)[:2000]}}]}


def row_props(r: dict) -> dict:
    url = r.get("url") or ""
    if url and not url.startswith("http"):
        url = ""
    props = {
        "Name": {"title": [{"type": "text", "text": {"content": r["name"][:200]}}]},
        "Slug": rt(r.get("slug", "")),
        "Category Label": rt(r.get("category_label", "")),
        "Subcategory": rt(r.get("subcategory", "")),
        "Language": rt(r.get("language", "")),
        "Region": rt(r.get("region", "")),
        "Enabled": {"checkbox": bool(r.get("enabled"))},
        "API Key Env": rt(r.get("api_key_env", "")),
        "License Notes": rt(r.get("license_notes", "")),
        "Section": rt(r.get("section", "")),
        "Source File": rt(r.get("source_file", "")),
    }
    cat = r.get("category", "other")
    if cat in [o["name"] for o in DB_PROPERTIES["Category"]["select"]["options"]]:
        props["Category"] = {"select": {"name": cat}}
    typ = r.get("type", "unknown")
    valid_types = [o["name"] for o in DB_PROPERTIES["Type"]["select"]["options"]]
    props["Type"] = {"select": {"name": typ if typ in valid_types else "unknown"}}
    props["Tier"] = {"select": {"name": str(r.get("tier", 1))}}
    if url:
        props["URL"] = {"url": url}
    return props


def create_database(notion: Client, parent_page_id: str) -> str:
    parent_page_id = parent_page_id.replace("-", "")
    db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": DB_TITLE}}],
        properties=DB_PROPERTIES,
    )
    return db["id"]


def query_existing_slugs(notion: Client, database_id: str) -> set[str]:
    slugs: set[str] = set()
    cursor = None
    while True:
        resp = notion.databases.query(database_id=database_id, start_cursor=cursor)
        for page in resp.get("results", []):
            for prop in page.get("properties", {}).values():
                if prop.get("type") == "rich_text" and prop.get("id"):
                    pass
            slug_prop = page.get("properties", {}).get("Slug", {})
            for t in slug_prop.get("rich_text", []):
                if t.get("plain_text"):
                    slugs.add(t["plain_text"])
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return slugs


def main() -> None:
    token = os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")
    if not token:
        print("Set NOTION_API_KEY (integration token)")
        sys.exit(1)
    if not JSON_PATH.exists():
        print(f"Run parse first: python scripts/parse-data-sources.py")
        sys.exit(1)

    records = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    notion = Client(auth=token)

    db_id = os.environ.get("NOTION_DATABASE_ID")
    parent = os.environ.get("NOTION_PARENT_PAGE_ID")
    if not db_id:
        if not parent:
            print("Set NOTION_PARENT_PAGE_ID (page to host new database) or NOTION_DATABASE_ID")
            sys.exit(1)
        print(f"Creating database '{DB_TITLE}'...")
        db_id = create_database(notion, parent)
        print(f"Created database: {db_id}")
        print(f"Share this page with your Notion integration!")
    else:
        db_id = db_id.replace("-", "")

    existing = query_existing_slugs(notion, db_id)
    created = updated = skipped = 0

    for r in records:
        slug = r.get("slug", "")
        if slug in existing:
            skipped += 1
            continue
        try:
            notion.pages.create(parent={"database_id": db_id}, properties=row_props(r))
            existing.add(slug)
            created += 1
            if created % 10 == 0:
                print(f"  ... {created} created")
            time.sleep(0.35)
        except APIResponseError as e:
            print(f"FAIL {r['name']}: {e}")

    print(f"Done: created={created}, skipped={skipped}, total={len(records)}")
    print(f"Database: https://www.notion.so/{db_id.replace('-', '')}")


if __name__ == "__main__":
    main()
