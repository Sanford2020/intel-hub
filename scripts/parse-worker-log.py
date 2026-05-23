#!/usr/bin/env python3
"""Parse Celery worker log for OPS-03 task execution counts."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


RECEIVED = re.compile(r"Received task: (?P<task>[\w\.]+)")
SUCCEEDED = re.compile(r"Task (?P<task>[\w\.]+)\[(?P<id>[^\]]+)\] succeeded")
FAILED = re.compile(r"Task (?P<task>[\w\.]+)\[(?P<id>[^\]]+)\] raised")
FAIL_REASON = re.compile(r"(HTTPError|404|SSL|timeout|ParseError|Invalid XML|ConnectionError|403)[^\n]*", re.I)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", default="docs/operations/worker-observation-2026-05-worker.log")
    args = parser.parse_args()
    text = Path(args.log).read_text(encoding="utf-8", errors="replace")

    received = Counter(m.group("task") for m in RECEIVED.finditer(text))
    succeeded = Counter(m.group("task") for m in SUCCEEDED.finditer(text))
    failed = Counter(m.group("task") for m in FAILED.finditer(text))
    reasons = Counter(m.group(0)[:120] for m in FAIL_REASON.finditer(text))

    print("=== Task received ===")
    for task, count in received.most_common():
        print(f"{count:5d}  {task}")

    print("\n=== Task succeeded ===")
    for task, count in succeeded.most_common():
        print(f"{count:5d}  {task}")

    print("\n=== Task failed (raised) ===")
    for task, count in failed.most_common():
        print(f"{count:5d}  {task}")

    print("\n=== Top failure snippets ===")
    for reason, count in reasons.most_common(5):
        print(f"{count:5d}  {reason}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
