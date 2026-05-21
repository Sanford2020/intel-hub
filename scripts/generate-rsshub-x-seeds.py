#!/usr/bin/env python3
"""Generate RSSHub-backed RSS sources from x-curated-accounts.json."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "seeds" / "x-curated-accounts.json"
DEFAULT_OUT = ROOT / "seeds" / "rsshub-x-sources.json"

_X_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:twitter|x)\.com/(?P<user>[A-Za-z0-9_]{1,15})(?:/|$|\?)",
    re.I,
)
_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{1,15}$")


def parse_x_username(raw: str) -> str:
    value = raw.strip()
    if not value:
        raise ValueError("Empty X handle")
    if value.startswith("@"):
        value = value[1:]
    match = _X_URL_RE.match(value)
    if match:
        return match.group("user")
    if _USERNAME_RE.fullmatch(value):
        return value
    raise ValueError(f"Cannot parse X username from: {raw!r}")


def _slugify(handle: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", handle.lower()).strip("-")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RSSHub X RSS seed file")
    parser.add_argument("--input", type=Path, default=DEFAULT_IN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--base",
        default=os.environ.get("RSSHUB_BASE_URL", "http://localhost:1200"),
        help="RSSHub base URL",
    )
    args = parser.parse_args()

    rows = json.loads(args.input.read_text(encoding="utf-8"))
    base = args.base.rstrip("/")
    out: list[dict] = []

    for row in rows:
        if row.get("type") != "x" or not row.get("url"):
            continue
        handle = parse_x_username(row["url"])
        slug = f"rsshub-x-{_slugify(handle)}"
        out.append(
            {
                "name": f"RSSHub X — @{handle}",
                "slug": slug,
                "category": row.get("category", "social"),
                "category_label": row.get("category_label"),
                "subcategory": "RSSHub X",
                "section": row.get("section"),
                "type": "rss",
                "url": f"{base}/twitter/user/{handle}",
                "language": row.get("language", "en"),
                "region": row.get("region", "global"),
                "tier": row.get("tier", 0),
                "enabled": bool(row.get("enabled", False)),
                "license_notes": f"RSSHub timeline for @{handle} (requires self-hosted RSSHub)",
                "source_file": "rsshub-x-sources.json",
            }
        )

    args.output.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(out)} sources → {args.output}")


if __name__ == "__main__":
    main()
