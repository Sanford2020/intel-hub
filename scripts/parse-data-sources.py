#!/usr/bin/env python3
"""Parse docs/project/data-sources/*.md into JSON + CSV for Notion import."""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "project" / "data-sources"
OUT = ROOT / "seeds"

FILE_CATEGORY = {
    "01-global-news-wire.md": ("wire", "通讯社/主流"),
    "02-regional-by-geography.md": ("regional", "分地区"),
    "03-government-official.md": ("official", "政府/机构"),
    "04-financial-economic.md": ("financial", "财经"),
    "05-osint-geopolitical.md": ("geopolitical", "OSINT/地缘"),
    "06-cyber-threat-intel.md": ("cyber", "网安"),
    "07-social-sentiment-ugc.md": ("social", "社交/UGC"),
    "08-academic-research-patents.md": ("research", "学术/专利"),
    "09-industry-verticals.md": ("vertical", "垂直行业"),
    "10-aggregators-apis.md": ("aggregator", "聚合/API"),
    "11-maritime-aviation-satellite.md": ("maritime", "海事/航空/卫星"),
    "12-sanctions-legal-pep.md": ("compliance", "制裁/法律"),
    "13-humanitarian-disaster-weather.md": ("humanitarian", "人道/灾害"),
    "14-china-greater-china.md": ("china", "大中华区"),
    "15-think-tanks-policy.md": ("thinktank", "智库"),
}

SKIP_FILES = {
    "README.md",
    "source-schema.md",
    "priority-matrix.md",
    "00-intelligence-taxonomy.md",
    "tier-0-mvp-seed.md",
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    return text.strip("-")[:80] or "source"


def parse_table_row(line: str) -> list[str] | None:
    if not line.startswith("|") or line.count("|") < 3:
        return None
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def is_separator(line: str) -> bool:
    return bool(re.match(r"^\|\s*[-:]+", line))


def infer_type(url: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit.lower().replace(" ", "_")
    u = (url or "").lower()
    if "gdelt" in u:
        return "gdelt"
    if "acled" in u:
        return "acled"
    if u.startswith("http"):
        if ".json" in u or "/api/" in u:
            return "rest_api"
        return "rss"
    if explicit := (explicit or ""):
        return explicit
    return "unknown"


def parse_markdown_file(path: Path, category: str, category_label: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    records: list[dict] = []
    section = ""
    headers: list[str] = []
    in_table = False

    for line in lines:
        if line.startswith("## "):
            section = line[3:].strip()
            in_table = False
            continue
        if line.startswith("|"):
            if is_separator(line):
                in_table = True
                continue
            cells = parse_table_row(line)
            if not cells:
                continue
            if not in_table:
                headers = [h.lower().replace(" ", "_").replace("/", "_") for h in cells]
                continue
            row = dict(zip(headers, cells + [""] * max(0, len(headers) - len(cells))))
            name = row.get("name") or row.get("platform") or row.get("tool") or row.get("slug")
            if not name or name.lower() in ("name", "slug", "platform"):
                continue
            if set(cells) <= {"---", ""}:
                continue

            url = (
                row.get("url")
                or row.get("feed")
                or row.get("feed___api")
                or row.get("feed___url")
                or row.get("api")
                or row.get("api___feed")
                or row.get("url___feed")
                or row.get("source")
                or row.get("pattern")
                or row.get("query")
                or ""
            )
            url = url.replace("feed / api", "").strip()
            if url in ("—", "-", "付费", "RSS", "API 付费", "web/API"):
                url = ""

            tier_raw = row.get("tier", "")
            tier_match = re.search(r"[012]", tier_raw)
            tier = int(tier_match.group()) if tier_match else 1

            lang = row.get("lang") or row.get("language") or ""
            typ = row.get("type") or row.get("api") if row.get("type") else None
            if row.get("type") and row["type"] not in ("rss", "rest_api", "gdelt", "acled"):
                pass
            source_type = infer_type(url, row.get("type"))

            slug = row.get("slug") or slugify(name)
            subcategory = row.get("category") or row.get("focus") or section

            records.append(
                {
                    "name": name,
                    "slug": slug,
                    "category": category,
                    "category_label": category_label,
                    "subcategory": subcategory,
                    "section": section,
                    "type": source_type,
                    "url": url,
                    "language": lang or "multi",
                    "region": row.get("region", "global"),
                    "tier": tier,
                    "license_notes": row.get("notes", ""),
                    "api_key_env": row.get("api_key_env", ""),
                    "source_file": path.name,
                    "enabled": tier == 0,
                }
            )
        else:
            in_table = False
            headers = []

    return records


def dedupe(records: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for r in records:
        key = r["slug"]
        if key in seen:
            key = f"{key}-{r['category']}"
        if key in seen:
            continue
        seen.add(key)
        r["slug"] = key
        out.append(r)
    return out


def main() -> None:
    all_records: list[dict] = []
    for md in sorted(DOCS.glob("*.md")):
        if md.name in SKIP_FILES:
            continue
        cat, label = FILE_CATEGORY.get(md.name, ("other", md.stem))
        all_records.extend(parse_markdown_file(md, cat, label))

    all_records = dedupe(all_records)
    OUT.mkdir(parents=True, exist_ok=True)

    json_path = OUT / "all-sources.json"
    csv_path = OUT / "all-sources.csv"
    json_path.write_text(json.dumps(all_records, ensure_ascii=False, indent=2), encoding="utf-8")

    fields = [
        "name",
        "slug",
        "category",
        "category_label",
        "subcategory",
        "type",
        "url",
        "language",
        "region",
        "tier",
        "enabled",
        "api_key_env",
        "license_notes",
        "section",
        "source_file",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in all_records:
            w.writerow(r)

    tier0 = sum(1 for r in all_records if r["tier"] == 0)
    print(f"Parsed {len(all_records)} sources ({tier0} tier-0)")
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")


if __name__ == "__main__":
    main()
