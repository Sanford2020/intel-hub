#!/usr/bin/env python3
"""Load a Notion MCP chunk payload by index (000-019) and print JSON to stdout."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "seeds" / "notion-mcp-chunks"


def main() -> None:
    idx = sys.argv[1] if len(sys.argv) > 1 else "000"
    path = CHUNKS / f"_call-{idx}.json"
    if not path.exists():
        path = CHUNKS / f"chunk-{idx}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        payload = {
            "parent": {
                "data_source_id": "9a37237d-4529-821f-97b7-077d5f5dc1c5",
                "type": "data_source_id",
            },
            "pages": data["pages"],
        }
    else:
        payload = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
