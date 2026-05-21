#!/usr/bin/env python3
"""Export notion-mcp-chunks to _call-NNN.json payloads for MCP import."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "seeds" / "notion-mcp-chunks"
PARENT = {
    "data_source_id": "9a37237d-4529-821f-97b7-077d5f5dc1c5",
    "type": "data_source_id",
}


def main() -> None:
    for path in sorted(CHUNKS.glob("chunk-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        out = {"parent": PARENT, "pages": data["pages"]}
        out_path = CHUNKS / f"_call-{path.stem.split('-')[-1]}.json"
        out_path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        print(out_path.name, len(data["pages"]))


if __name__ == "__main__":
    main()
