"""Dispatch intelligence analysis for articles missing reports."""

from __future__ import annotations

from sqlalchemy import select

from app.core.logging import get_logger
from app.db.sync_session import get_sync_session
from app.models.article import Article
from app.models.intelligence_report import IntelligenceReport
from app.models.source import Source
from workers.celery_app import celery_app
from workers.tasks.analyze.summarize import analyze_article

logger = get_logger(__name__)

BATCH_SIZE = 20


@celery_app.task(name="workers.tasks.analyze.dispatch.dispatch_unanalyzed_articles")
def dispatch_unanalyzed_articles() -> dict[str, int | list[int]]:
    with get_sync_session() as session:
        rows = session.execute(
            select(Article.id)
            .join(Source, Source.id == Article.source_id)
            .outerjoin(
                IntelligenceReport,
                IntelligenceReport.article_id == Article.id,
            )
            .where(
                Source.enabled.is_(True),
                Source.tier == 0,
                IntelligenceReport.id.is_(None),
            )
            .order_by(Article.id.desc())
            .limit(BATCH_SIZE)
        )
        article_ids = [row[0] for row in rows.all()]

    for article_id in article_ids:
        analyze_article.delay(article_id)

    logger.info("dispatch_unanalyzed_articles.queued", count=len(article_ids))
    return {"queued": len(article_ids), "article_ids": article_ids}
