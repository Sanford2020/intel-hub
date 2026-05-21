#!/usr/bin/env python3
"""Export tier-0 enabled sources from all-sources.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALL = ROOT / "seeds" / "all-sources.json"
OUT = ROOT / "seeds" / "tier-0-sources.json"


def main() -> None:
    if not ALL.exists():
        raise SystemExit(f"Missing {ALL}. Run: python scripts/parse-data-sources.py")
    rows = json.loads(ALL.read_text(encoding="utf-8"))
    tier0 = [r for r in rows if r.get("tier") == 0]
    OUT.write_text(json.dumps(tier0, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(tier0)} tier-0 sources -> {OUT}")


if __name__ == "__main__":
    main()
