import math
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.config import settings
from app.models.user import User
from app.modules.auth.dependencies import require_admin, require_operator_write
from app.modules.articles.schemas import (
    ArticleCreate,
    ArticleListResponse,
    ArticleRead,
    ArticleUpdate,
)
from app.modules.articles.service import ArticleService, article_to_read
from app.modules.alerts.service import AlertService
from app.modules.intelligence.analyzer import analyze_article_async, get_report_for_article
from app.modules.intelligence.schemas import AnalyzeArticleResponse, IntelligenceReportRead

router = APIRouter(prefix="/articles", tags=["articles"])


def get_article_service(session: AsyncSession = Depends(get_session)) -> ArticleService:
    return ArticleService(session)


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_id: int | None = None,
    tag: str | None = None,
    published_from: datetime | None = None,
    published_to: datetime | None = None,
    has_report: bool | None = None,
    min_relevance: float | None = Query(None, ge=0.0, le=10.0),
    q: str | None = None,
    service: ArticleService = Depends(get_article_service),
) -> ArticleListResponse:
    rows, total = await service.list(
        page=page,
        page_size=page_size,
        source_id=source_id,
        tag=tag,
        published_from=published_from,
        published_to=published_to,
        has_report=has_report,
        min_relevance=min_relevance,
        q=q,
    )
    total_pages = math.ceil(total / page_size) if total else 0
    return ArticleListResponse(
        data=[article_to_read(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=ArticleRead, status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: ArticleCreate,
    _user: User = Depends(require_admin),
    service: ArticleService = Depends(get_article_service),
) -> ArticleRead:
    article = await service.create(payload)
    return ArticleRead.model_validate(article)


@router.get("/{article_id}", response_model=ArticleRead)
async def get_article(
    article_id: int,
    service: ArticleService = Depends(get_article_service),
) -> ArticleRead:
    article = await service.get(article_id)
    return article_to_read(article)


@router.patch("/{article_id}", response_model=ArticleRead)
async def update_article(
    article_id: int,
    payload: ArticleUpdate,
    _user: User = Depends(require_admin),
    service: ArticleService = Depends(get_article_service),
) -> ArticleRead:
    article = await service.update(article_id, payload)
    return article_to_read(article)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    _user: User = Depends(require_admin),
    service: ArticleService = Depends(get_article_service),
) -> None:
    await service.delete(article_id)


@router.post("/{article_id}/analyze", response_model=AnalyzeArticleResponse)
async def analyze_article(
    article_id: int,
    _user: User = Depends(require_operator_write),
    session: AsyncSession = Depends(get_session),
) -> AnalyzeArticleResponse:
    """Run AI intelligence analysis and upsert IntelligenceReport."""
    report = await analyze_article_async(session, article_id)
    try:
        await AlertService(session).evaluate_article(article_id)
    except Exception:  # noqa: BLE001
        pass
    return AnalyzeArticleResponse(
        data=IntelligenceReportRead.model_validate(report)
    )


@router.get("/{article_id}/report", response_model=AnalyzeArticleResponse)
async def get_article_report(
    article_id: int,
    session: AsyncSession = Depends(get_session),
) -> AnalyzeArticleResponse:
    report = await get_report_for_article(session, article_id)
    return AnalyzeArticleResponse(
        data=IntelligenceReportRead.model_validate(report)
    )
