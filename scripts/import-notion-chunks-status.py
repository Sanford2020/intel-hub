#!/usr/bin/env python3
"""
Print MCP import instructions / payload paths for notion-create-pages batches.

Usage:
  python scripts/import-notion-chunks-status.py          # summary
  python scripts/import-notion-chunks-status.py --chunk 002  # one payload
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "seeds" / "notion-mcp-chunks"
PROGRESS = CHUNKS / ".import-progress.json"
PARENT = {
    "data_source_id": "9a37237d-4529-821f-97b7-077d5f5dc1c5",
    "type": "data_source_id",
}


def load_progress() -> set[str]:
    if PROGRESS.exists():
        return set(json.loads(PROGRESS.read_text(encoding="utf-8")))
    return set()


def save_progress(done: set[str]) -> None:
    PROGRESS.write_text(json.dumps(sorted(done), indent=2), encoding="utf-8")


def chunk_ids() -> list[str]:
    return sorted(p.stem.replace("_call-", "") for p in CHUNKS.glob("_call-*.json"))


def payload(idx: str) -> dict:
    data = json.loads((CHUNKS / f"_call-{idx}.json").read_text(encoding="utf-8"))
    return {"parent": PARENT, "pages": data["pages"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk", help="Print JSON payload for chunk id e.g. 002")
    parser.add_argument("--mark", help="Mark chunk id as imported")
    args = parser.parse_args()

    if args.mark:
        done = load_progress()
        done.add(args.mark)
        save_progress(done)
        print(f"marked {args.mark}, total {len(done)}")
        return

    if args.chunk:
        print(json.dumps(payload(args.chunk), ensure_ascii=False))
        return

    done = load_progress()
    ids = chunk_ids()
    pending = [i for i in ids if i not in done]
    print(f"total_chunks={len(ids)} done={len(done)} pending={len(pending)}")
    if pending:
        print("pending:", ",".join(pending))


if __name__ == "__main__":
    main()
