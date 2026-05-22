#!/usr/bin/env python
"""Probe enabled RSS seed sources and write a health report."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import socket
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "seeds"
DEFAULT_OUT = ROOT / "docs" / "operations" / "rss-health-2026-05.md"
USER_AGENT = "IntelHubRSSHealth/1.0 (+local ops probe)"


@dataclass(frozen=True)
class Source:
    slug: str
    name: str
    url: str
    file: Path
    row_index: int
    category: str
    tier: Any


@dataclass
class Attempt:
    ok: bool
    status: int | None
    elapsed_ms: int
    final_url: str
    entries: int
    error_type: str
    error: str


@dataclass
class Result:
    source: Source
    attempts: list[Attempt]

    @property
    def ok(self) -> bool:
        return any(attempt.ok for attempt in self.attempts)

    @property
    def final(self) -> Attempt:
        return self.attempts[-1]

    @property
    def error_type(self) -> str:
        if self.ok:
            return "ok"
        return self.final.error_type


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe enabled RSS seed health")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--apply-disabled",
        action="store_true",
        help="Set enabled=false in seed rows that failed all attempts.",
    )
    return parser.parse_args()


def load_sources() -> list[Source]:
    seen: set[str] = set()
    sources: list[Source] = []

    for path in sorted(SEEDS.glob("*.json")):
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(rows, list):
            continue

        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            if not row.get("enabled"):
                continue
            source_type = row.get("type") or row.get("source_type")
            if source_type != "rss":
                continue
            url = str(row.get("url") or "").strip()
            slug = str(row.get("slug") or "").strip()
            if not url or not slug or slug in seen:
                continue
            seen.add(slug)
            sources.append(
                Source(
                    slug=slug,
                    name=str(row.get("name") or slug),
                    url=url,
                    file=path,
                    row_index=index,
                    category=str(row.get("category") or ""),
                    tier=row.get("tier", ""),
                )
            )

    return sources


def classify_http_status(status: int | None) -> str:
    if status is None:
        return "network"
    if 400 <= status < 500:
        return "http_4xx"
    if 500 <= status < 600:
        return "http_5xx"
    return "http_status"


def count_feed_entries(content: bytes) -> tuple[bool, int, str]:
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        return False, 0, f"XML parse error: {exc}"

    root_name = root.tag.rsplit("}", 1)[-1].lower()
    if root_name not in {"rss", "feed", "rdf"}:
        return False, 0, f"Unexpected XML root: {root.tag}"

    entries = 0
    for element in root.iter():
        name = element.tag.rsplit("}", 1)[-1].lower()
        if name in {"item", "entry"}:
            entries += 1

    if entries == 0:
        return False, 0, "Feed parsed but had no item/entry elements"
    return True, entries, ""


def probe_once(source: Source, timeout: float) -> Attempt:
    started = time.perf_counter()
    request = urllib.request.Request(source.url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.getcode()
            final_url = response.geturl()
            content = response.read(2_000_000)
    except urllib.error.HTTPError as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return Attempt(
            ok=False,
            status=exc.code,
            elapsed_ms=elapsed_ms,
            final_url=exc.url or source.url,
            entries=0,
            error_type=classify_http_status(exc.code),
            error=str(exc),
        )
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        reason = getattr(exc, "reason", exc)
        error = str(reason)
        error_type = "timeout" if "timed out" in error.lower() else "network"
        return Attempt(
            ok=False,
            status=None,
            elapsed_ms=elapsed_ms,
            final_url=source.url,
            entries=0,
            error_type=error_type,
            error=error,
        )
    except Exception as exc:  # noqa: BLE001 - report unexpected probe errors.
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return Attempt(
            ok=False,
            status=None,
            elapsed_ms=elapsed_ms,
            final_url=source.url,
            entries=0,
            error_type="probe_error",
            error=f"{type(exc).__name__}: {exc}",
        )

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    if status >= 400:
        return Attempt(
            ok=False,
            status=status,
            elapsed_ms=elapsed_ms,
            final_url=final_url,
            entries=0,
            error_type=classify_http_status(status),
            error=f"HTTP {status}",
        )

    parsed, entries, parse_error = count_feed_entries(content)
    if not parsed:
        return Attempt(
            ok=False,
            status=status,
            elapsed_ms=elapsed_ms,
            final_url=final_url,
            entries=entries,
            error_type="parse_failed",
            error=parse_error,
        )

    return Attempt(
        ok=True,
        status=status,
        elapsed_ms=elapsed_ms,
        final_url=final_url,
        entries=entries,
        error_type="ok",
        error="",
    )


def probe_source(source: Source, timeout: float) -> Result:
    attempts = [probe_once(source, timeout)]
    if not attempts[0].ok:
        attempts.append(probe_once(source, timeout))
    return Result(source=source, attempts=attempts)


def summarize(results: list[Result]) -> dict[str, int]:
    summary = {
        "total": len(results),
        "ok": 0,
        "timeout": 0,
        "parse_failed": 0,
        "http_4xx": 0,
        "http_5xx": 0,
        "network": 0,
        "other_failed": 0,
        "redirected": 0,
    }

    for result in results:
        if result.ok:
            summary["ok"] += 1
        elif result.error_type in summary:
            summary[result.error_type] += 1
        else:
            summary["other_failed"] += 1
        if result.final.final_url and result.final.final_url != result.source.url:
            summary["redirected"] += 1

    return summary


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(escape_cell(value) for value in row) + " |")
    return "\n".join(lines)


def escape_cell(value: Any) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def write_report(results: list[Result], out: Path, apply_disabled: bool) -> None:
    summary = summarize(results)
    failed = [result for result in results if not result.ok]
    ok = [result for result in results if result.ok]
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    lines = [
        "# RSS Health Report — 2026-05",
        "",
        f"- Generated: {generated}",
        "- Network context: localnet probe from current operator machine.",
        "- Failure policy: a source is failed only when both attempts fail.",
        f"- Seed update mode: {'applied enabled=false' if apply_disabled else 'report only'}",
        "",
        "## Summary",
        "",
        markdown_table(
            [
                ["Total enabled RSS", summary["total"]],
                ["OK", summary["ok"]],
                ["Timeout", summary["timeout"]],
                ["Parse failed", summary["parse_failed"]],
                ["HTTP 4xx", summary["http_4xx"]],
                ["HTTP 5xx", summary["http_5xx"]],
                ["Network", summary["network"]],
                ["Other failed", summary["other_failed"]],
                ["Redirected", summary["redirected"]],
            ],
            ["Metric", "Count"],
        ),
        "",
        "## Recommended Disabled",
        "",
    ]

    if failed:
        lines.append(
            markdown_table(
                [
                    [
                        result.source.slug,
                        result.source.name,
                        result.source.file.name,
                        result.error_type,
                        result.final.status or "",
                        result.final.error,
                        "unknown",
                        result.source.url,
                    ]
                    for result in failed
                ],
                [
                    "Slug",
                    "Name",
                    "Seed",
                    "Error Type",
                    "HTTP",
                    "Error",
                    "Last Success",
                    "URL",
                ],
            )
        )
    else:
        lines.append("No sources met the two-attempt failure threshold.")

    lines.extend(["", "## OK Sources", ""])
    lines.append(
        markdown_table(
            [
                [
                    result.source.slug,
                    result.source.name,
                    result.source.file.name,
                    result.final.status or "",
                    result.final.entries,
                    result.final.elapsed_ms,
                    "yes" if result.final.final_url != result.source.url else "no",
                ]
                for result in ok
            ],
            ["Slug", "Name", "Seed", "HTTP", "Entries", "Latency ms", "Redirected"],
        )
    )

    lines.extend(["", "## All Probe Results", ""])
    lines.append(
        markdown_table(
            [
                [
                    result.source.slug,
                    "PASS" if result.ok else "FAIL",
                    result.error_type,
                    len(result.attempts),
                    result.final.status or "",
                    result.final.entries,
                    result.final.elapsed_ms,
                    result.source.url,
                ]
                for result in results
            ],
            ["Slug", "Result", "Type", "Attempts", "HTTP", "Entries", "Latency ms", "URL"],
        )
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply_disabled_flags(failed: list[Result]) -> dict[str, int]:
    failed_slugs = {result.source.slug for result in failed}
    changed_by_file: dict[str, int] = {}

    for path in sorted(SEEDS.glob("*.json")):
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(rows, list):
            continue

        changed = 0
        for row in rows:
            if not isinstance(row, dict):
                continue
            if row.get("slug") in failed_slugs and row.get("enabled") is True:
                row["enabled"] = False
                changed += 1

        if changed:
            path.write_text(
                json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            changed_by_file[path.name] = changed

    return changed_by_file


def main() -> int:
    args = parse_args()
    sources = load_sources()
    if not sources:
        raise SystemExit("No enabled RSS sources found in seeds/*.json")

    print(f"Probing {len(sources)} enabled RSS sources...")
    results: list[Result] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        future_to_source = {
            pool.submit(probe_source, source, args.timeout): source for source in sources
        }
        for future in concurrent.futures.as_completed(future_to_source):
            result = future.result()
            results.append(result)
            status = "PASS" if result.ok else "FAIL"
            print(f"{status} {result.source.slug} ({result.error_type})")

    results.sort(key=lambda result: result.source.slug)
    failed = [result for result in results if not result.ok]
    changed = apply_disabled_flags(failed) if args.apply_disabled else {}
    write_report(results, args.out, args.apply_disabled)

    print(f"Wrote report: {args.out}")
    if args.apply_disabled:
        print(f"Updated enabled flags: {changed or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
