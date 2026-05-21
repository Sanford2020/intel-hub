#!/usr/bin/env python3
"""Load chunk payloads for Notion MCP import (chunks 002-019)."""
import json
import sys
from pathlib import Path

PARENT = {
    "data_source_id": "9a37237d-4529-821f-97b7-077d5f5dc1c5",
    "type": "data_source_id",
}
BASE = Path(__file__).resolve().parent
LOG = BASE / "import-results.jsonl"


def load_chunk(n: int) -> dict:
    path = BASE / f"chunk-{n:03d}.json"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return {"parent": PARENT, "pages": data["pages"]}


def log(n: int, ok: bool, count: int, err: str | None = None) -> None:
    entry = {"chunk": n, "attempted": count, "success": ok, "created": count if ok else 0, "error": err}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(json.dumps(entry))


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: run_mcp_import.py dump <n> | log <n> <ok> [error]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "dump":
        n = int(sys.argv[2])
        out = BASE / ".payloads" / f"chunk-{n:03d}.json"
        if not out.exists():
            payload = load_chunk(n)
            out.parent.mkdir(exist_ok=True)
            out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        print(out)
        return
    if cmd == "log":
        n, ok = int(sys.argv[2]), sys.argv[3].lower() == "true"
        err = sys.argv[4] if len(sys.argv) > 4 else None
        log(n, ok, 25, err)
        return
    if cmd == "summary":
        rows = []
        total = 0
        if LOG.exists():
            for line in LOG.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    e = json.loads(line)
                    rows.append(e)
                    if e.get("success"):
                        total += e.get("created", 0)
        print(json.dumps({"rows": rows, "total": total}, indent=2))
        return
    print(f"unknown: {cmd}")
    sys.exit(1)


if __name__ == "__main__":
    main()
