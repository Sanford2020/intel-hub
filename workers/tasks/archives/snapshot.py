"""Daily archive Celery task."""

from __future__ import annotations

from app.config import settings
from app.core.logging import get_logger
from app.db.sync_session import get_sync_session
from app.modules.archives.service import create_or_update_daily_archive_sync
from workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="workers.tasks.archives.snapshot.archive_daily_snapshot")
def archive_daily_snapshot() -> dict:
    if not settings.archive_enabled:
        logger.info("archive_daily_snapshot.skipped", reason="ARCHIVE_ENABLED=false")
        return {"status": "skipped", "reason": "disabled"}

    with get_sync_session() as session:
        record = create_or_update_daily_archive_sync(session)
        payload = {
            "status": record.status,
            "archive_date": record.archive_date.isoformat(),
            "timezone": record.timezone,
        }
        logger.info("archive_daily_snapshot.done", **payload)
        return payload
