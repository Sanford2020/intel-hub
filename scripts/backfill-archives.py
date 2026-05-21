#!/usr/bin/env python3
"""Backfill daily_archives for past N Beijing calendar days."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

_REPO = Path(__file__).resolve().parents[1]
_BACKEND = _REPO / "backend"
# backend/ must precede repo root so `app` resolves correctly when cwd is not backend/
for path in (_REPO, _BACKEND):
    s = str(path)
    if s not in sys.path:
        sys.path.insert(0, s)

from app.config import settings
from app.db.sync_session import get_sync_session
from app.modules.archives.service import create_or_update_daily_archive_sync


def _utc_noon_for_beijing_day(day: date) -> datetime:
    """Pick a stable UTC instant inside the Beijing calendar day for window anchoring."""
    tz = ZoneInfo(settings.archive_timezone)
    local = datetime(day.year, day.month, day.day, 12, 0, tzinfo=tz)
    return local.astimezone(UTC)


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill daily archive snapshots")
    parser.add_argument("--days", type=int, default=7, help="Number of past days including today")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not settings.archive_enabled:
        print("ARCHIVE_ENABLED=false — enable in .env first", file=sys.stderr)
        return 1

    tz = ZoneInfo(settings.archive_timezone)
    today = datetime.now(tz).date()
    targets = [today - timedelta(days=offset) for offset in range(args.days - 1, -1, -1)]

    if args.dry_run:
        print(f"Would backfill {len(targets)} days: {targets[0]} .. {targets[-1]} ({settings.archive_timezone})")
        return 0

    ok = 0
    failed = 0
    with get_sync_session() as session:
        for day in targets:
            try:
                record = create_or_update_daily_archive_sync(
                    session,
                    archive_date=day,
                    now=_utc_noon_for_beijing_day(day),
                )
                session.commit()
                heat = (record.metrics_json or {}).get("category_heat") or []
                top = heat[0]["category"] if heat else "—"
                print(f"OK {day} status={record.status} items={(record.metrics_json or {}).get('briefing_meta', {}).get('item_count', '?')} top={top}")
                ok += 1
            except Exception as exc:  # noqa: BLE001
                session.rollback()
                print(f"FAIL {day}: {exc}", file=sys.stderr)
                failed += 1

    print(f"\nBackfill done: {ok} ok, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
