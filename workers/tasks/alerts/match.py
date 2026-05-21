"""Alert evaluation Celery tasks."""

from __future__ import annotations

from app.core.logging import get_logger
from app.db.sync_session import get_sync_session
from app.modules.alerts.service import evaluate_alerts_for_article_sync
from workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    name="workers.tasks.alerts.match.evaluate_alerts_for_article",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def evaluate_alerts_for_article(article_id: int) -> dict:
    logger.info("evaluate_alerts.start", article_id=article_id)
    with get_sync_session() as session:
        result = evaluate_alerts_for_article_sync(session, article_id)
    payload = {
        "article_id": result.article_id,
        "events_created": result.events_created,
    }
    logger.info("evaluate_alerts.done", **payload)
    return payload
