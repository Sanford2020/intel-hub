#!/usr/bin/env python3
"""Build Notion page payloads from all-sources.json for MCP batch import."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "seeds" / "all-sources.json"
OUT = ROOT / "seeds" / "notion-batches"

TYPE_MAP = {
    "rss": "新闻RSS",
    "rest_api": "其他",
    "gdelt": "其他",
    "acled": "其他",
    "telegram": "社区",
    "scraper": "其他",
    "unknown": "其他",
}

CATEGORY_LABEL = {
    "wire": "wire",
    "regional": "regional",
    "official": "official",
    "financial": "financial",
    "geopolitical": "geopolitical",
    "cyber": "cyber",
    "social": "social",
    "research": "research",
    "vertical": "vertical",
    "aggregator": "aggregator",
    "maritime": "maritime",
    "compliance": "compliance",
    "humanitarian": "humanitarian",
    "china": "china",
    "thinktank": "thinktank",
    "other": "other",
}

FREQ_MAP = {0: "每15分钟", 1: "每30分钟", 2: "每日"}


def map_source_type(r: dict) -> str:
    if r.get("category") == "social":
        name = r.get("name", "").lower()
        if "reddit" in name or "reddit" in r.get("url", "").lower():
            return "Reddit"
        if "twitter" in name or "x " in name:
            return "Twitter/X"
        return "社区"
    if r.get("category") in ("research", "thinktank", "vertical"):
        return "行业报告"
    return TYPE_MAP.get(r.get("type", "unknown"), "其他")


def to_page(r: dict) -> dict:
    url = r.get("url") or ""
    if url and not url.startswith("http"):
        url = ""
    tier = r.get("tier", 1)
    note_parts = [
        f"slug={r.get('slug', '')}",
        f"subcategory={r.get('subcategory', '')}",
        f"region={r.get('region', '')}",
    ]
    if r.get("api_key_env"):
        note_parts.append(f"api_key={r['api_key_env']}")
    if r.get("license_notes"):
        note_parts.append(r["license_notes"])

    props = {
        "来源名称": r["name"][:200],
        "Slug": r.get("slug", ""),
        "分类": CATEGORY_LABEL.get(r.get("category", "other"), "other"),
        "层级": f"Tier {tier}",
        "接入方式": r.get("type", "unknown") if r.get("type") in (
            "rss", "rest_api", "gdelt", "acled", "telegram", "scraper", "unknown"
        ) else "unknown",
        "语言": r.get("language", "multi"),
        "源文件": r.get("source_file", ""),
        "来源类型": map_source_type(r),
        "是否启用": "__YES__" if r.get("enabled") else "__NO__",
        "抓取频率": FREQ_MAP.get(tier, "每30分钟"),
        "可信度评分": max(1, 10 - tier * 2),
        "备注": " | ".join(p for p in note_parts if p),
    }
    if url:
        props["来源地址"] = url
    return {"properties": props}


def main() -> None:
    records = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    batch_size = 100
    batches = []
    for i in range(0, len(records), batch_size):
        chunk = records[i : i + batch_size]
        batches.append([to_page(r) for r in chunk])

    for idx, batch in enumerate(batches):
        path = OUT / f"batch-{idx:02d}.json"
        path.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{len(records)} records -> {len(batches)} batches in {OUT}")


if __name__ == "__main__":
    main()
