#!/usr/bin/env python3
"""Print MCP notion-create-pages arguments for a batch index (stdout JSON)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "seeds" / "notion-mcp-args"


def main() -> None:
    idx = int(sys.argv[1])
    path = ROOT / f"arg-{idx}.json"
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
