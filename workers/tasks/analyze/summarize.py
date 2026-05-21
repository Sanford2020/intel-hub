"""Article intelligence analysis Celery tasks."""

from __future__ import annotations

from app.core.logging import get_logger
from app.db.sync_session import get_sync_session
from app.modules.intelligence.analyzer import analyze_article_sync
from workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    name="workers.tasks.analyze.summarize.analyze_article",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=3,
)
def analyze_article(self, article_id: int) -> dict:  # type: ignore[no-untyped-def]
    logger.info("analyze_article.start", article_id=article_id, task_id=self.request.id)
    with get_sync_session() as session:
        result = analyze_article_sync(session, article_id)
    logger.info("analyze_article.done", **result.to_dict())
    return result.to_dict()
