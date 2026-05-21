#!/usr/bin/env python3
"""Import all notion-batches-small chunks via Notion MCP (run from Cursor agent)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHUNK_DIR = Path(__file__).resolve().parents[1] / "seeds" / "notion-batches-small"
PARENT = {"data_source_id": "9a37237d-4529-821f-97b7-077d5f5dc1c5", "type": "data_source_id"}
SKIP_SLUGS = {
    "war-on-the-rocks",
    "peterson-institute-piie",
    "nber-working-papers",
    "imf-research",
    "bis-working-papers",
    "cf40",
}


def load_chunks(skip_slugs: set[str]) -> list[dict]:
    payloads = []
    for path in sorted(CHUNK_DIR.glob("chunk-*.json")):
        pages = json.loads(path.read_text(encoding="utf-8"))
        if skip_slugs:
            pages = [p for p in pages if p.get("properties", {}).get("Slug") not in skip_slugs]
        if pages:
            payloads.append({"parent": PARENT, "pages": pages, "chunk": path.name})
    return payloads


def main() -> None:
    skip = SKIP_SLUGS if "--skip-imported" in sys.argv else set()
    payloads = load_chunks(skip)
    out = CHUNK_DIR / "import-manifest.json"
    out.write_text(json.dumps(payloads, ensure_ascii=False), encoding="utf-8")
    total = sum(len(p["pages"]) for p in payloads)
    print(f"manifest: {out}")
    print(f"chunks: {len(payloads)}, pages: {total}")


if __name__ == "__main__":
    main()
