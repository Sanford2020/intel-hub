from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ConflictError, NotFoundError
from app.models.article import Article
from app.models.intelligence_report import IntelligenceReport
from app.models.source import Source
from app.modules.articles.hashing import article_content_hash
from app.modules.articles.schemas import ArticleCreate, ArticleRead, ArticleUpdate, ReportSummary


def article_to_read(article: Article) -> ArticleRead:
    report = None
    if article.intelligence_report is not None:
        ir = article.intelligence_report
        report = ReportSummary(
            summary=ir.summary,
            tags=ir.tags or [],
            relevance_score=ir.relevance_score,
        )
    return ArticleRead.model_validate(
        {
            "id": article.id,
            "source_id": article.source_id,
            "title": article.title,
            "url": article.url,
            "content": article.content,
            "content_hash": article.content_hash,
            "published_at": article.published_at,
            "language": article.language,
            "created_at": article.created_at,
            "updated_at": article.updated_at,
            "report": report,
        }
    )


class ArticleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _ensure_source(self, source_id: int) -> None:
        if not await self.session.get(Source, source_id):
            raise NotFoundError(message=f"Source {source_id} not found")

    async def create(self, payload: ArticleCreate) -> Article:
        await self._ensure_source(payload.source_id)
        content_hash = article_content_hash(payload.title, payload.url)
        existing = await self.session.scalar(
            select(Article).where(Article.content_hash == content_hash)
        )
        if existing:
            raise ConflictError(
                message="Duplicate article",
                details={"content_hash": content_hash, "article_id": existing.id},
            )
        article = Article(
            **payload.model_dump(),
            content_hash=content_hash,
        )
        self.session.add(article)
        await self.session.flush()
        await self.session.refresh(article)
        return article

    async def get(self, article_id: int) -> Article:
        article = await self.session.scalar(
            select(Article)
            .where(Article.id == article_id)
            .options(selectinload(Article.intelligence_report))
        )
        if not article:
            raise NotFoundError(message=f"Article {article_id} not found")
        return article

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        source_id: int | None = None,
        tag: str | None = None,
        published_from: datetime | None = None,
        published_to: datetime | None = None,
        has_report: bool | None = None,
        min_relevance: float | None = None,
        q: str | None = None,
    ) -> tuple[list[Article], int]:
        query = select(Article).options(selectinload(Article.intelligence_report))

        needs_report_join = tag or has_report is not None or min_relevance is not None
        if needs_report_join:
            query = query.outerjoin(
                IntelligenceReport,
                IntelligenceReport.article_id == Article.id,
            )

        if source_id is not None:
            query = query.where(Article.source_id == source_id)
        if published_from is not None:
            query = query.where(Article.published_at >= published_from)
        if published_to is not None:
            query = query.where(Article.published_at <= published_to)
        if q:
            query = query.where(Article.title.ilike(f"%{q}%"))
        if tag:
            query = query.where(
                cast(IntelligenceReport.tags, String).like(f'%"{tag}"%')
            )
        if has_report is True:
            query = query.where(IntelligenceReport.id.isnot(None))
        elif has_report is False:
            query = query.where(IntelligenceReport.id.is_(None))
        if min_relevance is not None:
            query = query.where(
                IntelligenceReport.id.isnot(None),
                IntelligenceReport.relevance_score >= min_relevance,
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = int(await self.session.scalar(count_query) or 0)

        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size
        order = (
            [
                IntelligenceReport.relevance_score.desc(),
                Article.published_at.desc().nullslast(),
                Article.id.desc(),
            ]
            if min_relevance is not None
            else [Article.published_at.desc().nullslast(), Article.id.desc()]
        )
        rows = await self.session.scalars(
            query.order_by(*order).offset(offset).limit(page_size)
        )
        return list(rows.unique().all()), total

    async def update(self, article_id: int, payload: ArticleUpdate) -> Article:
        article = await self.get(article_id)
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(article, key, value)
        if "title" in data or "url" in data:
            article.content_hash = article_content_hash(article.title, article.url)
        await self.session.flush()
        await self.session.refresh(article)
        return article

    async def delete(self, article_id: int) -> None:
        article = await self.get(article_id)
        await self.session.delete(article)
