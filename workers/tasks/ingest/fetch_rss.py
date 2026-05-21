"""RSS ingestion Celery tasks."""

from __future__ import annotations

from app.core.logging import get_logger
from app.db.sync_session import get_sync_session
from app.modules.ingest.pipeline import ingest_source, list_due_source_ids
from workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    name="workers.tasks.ingest.fetch_rss.fetch_rss_for_source",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
)
def fetch_rss_for_source(self, source_id: int) -> dict:  # type: ignore[no-untyped-def]
    logger.info("fetch_rss_for_source.start", source_id=source_id, task_id=self.request.id)
    with get_sync_session() as session:
        result = ingest_source(session, source_id)
    payload = result.to_dict()
    if result.status == "success" and result.created_article_ids:
        from workers.tasks.analyze.summarize import analyze_article

        for article_id in result.created_article_ids:
            analyze_article.delay(article_id)
        logger.info(
            "fetch_rss_for_source.queued_analyze",
            source_id=source_id,
            article_ids=result.created_article_ids,
        )
    logger.info("fetch_rss_for_source.done", **payload)
    if result.status == "failed":
        raise RuntimeError(result.error_message or "RSS ingest failed")
    return result.to_dict()


@celery_app.task(name="workers.tasks.ingest.fetch_rss.dispatch_due_rss_sources")
def dispatch_due_rss_sources() -> dict[str, int | list[int]]:
    with get_sync_session() as session:
        due_ids = list_due_source_ids(session)
    for source_id in due_ids:
        fetch_rss_for_source.delay(source_id)
    logger.info("dispatch_due_rss_sources.queued", count=len(due_ids), source_ids=due_ids)
    return {"queued": len(due_ids), "source_ids": due_ids}
