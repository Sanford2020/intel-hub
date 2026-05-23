import math

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.db.sync_session import get_sync_session
from app.models.user import User
from app.modules.auth.dependencies import require_admin, require_operator_write
from app.modules.ingest.pipeline import ingest_source
from app.modules.sources.schemas import (
    IngestLogListResponse,
    IngestLogRead,
    IngestResultRead,
    SourceBulkImportRequest,
    SourceBulkImportResult,
    SourceCreate,
    SourceListResponse,
    SourceRead,
    SourceUpdate,
)
from app.modules.sources.service import SourceService

router = APIRouter(prefix="/sources", tags=["sources"])


def get_source_service(session: AsyncSession = Depends(get_session)) -> SourceService:
    return SourceService(session)


@router.get("", response_model=SourceListResponse)
async def list_sources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = None,
    tier: int | None = Query(default=None, ge=0, le=2),
    enabled: bool | None = None,
    service: SourceService = Depends(get_source_service),
) -> SourceListResponse:
    rows, total = await service.list(
        page=page,
        page_size=page_size,
        category=category,
        tier=tier,
        enabled=enabled,
    )
    total_pages = math.ceil(total / page_size) if total else 0
    return SourceListResponse(
        data=[SourceRead.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
async def create_source(
    payload: SourceCreate,
    _user: User = Depends(require_operator_write),
    service: SourceService = Depends(get_source_service),
) -> SourceRead:
    source = await service.create(payload)
    return SourceRead.model_validate(source)


@router.post("/import", response_model=SourceBulkImportResult)
async def import_sources(
    payload: SourceBulkImportRequest,
    _user: User = Depends(require_operator_write),
    service: SourceService = Depends(get_source_service),
) -> SourceBulkImportResult:
    return await service.bulk_import(payload)


@router.post("/{source_id}/ingest", response_model=IngestResultRead)
async def ingest_source_now(
    source_id: int,
    async_mode: bool = Query(False, alias="async"),
    _user: User = Depends(require_operator_write),
    service: SourceService = Depends(get_source_service),
) -> IngestResultRead:
    """Run ingest synchronously, or queue Celery task when async=1."""
    if async_mode:
        await service.get(source_id)
        from workers.tasks.ingest.fetch_rss import fetch_rss_for_source

        task = fetch_rss_for_source.delay(source_id)
        return IngestResultRead(source_id=source_id, status="queued", task_id=task.id)

    with get_sync_session() as session:
        result = ingest_source(session, source_id)
    if result.status == "success" and result.created_article_ids:
        from workers.tasks.analyze.summarize import analyze_article

        for article_id in result.created_article_ids:
            analyze_article.delay(article_id)
    return IngestResultRead.model_validate(result.to_dict())


@router.get("/{source_id}/ingest-logs", response_model=IngestLogListResponse)
async def list_source_ingest_logs(
    source_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: SourceService = Depends(get_source_service),
) -> IngestLogListResponse:
    rows, total = await service.list_ingest_logs(
        source_id, page=page, page_size=page_size
    )
    total_pages = math.ceil(total / page_size) if total else 0
    return IngestLogListResponse(
        data=[IngestLogRead.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{source_id}", response_model=SourceRead)
async def get_source(
    source_id: int,
    service: SourceService = Depends(get_source_service),
) -> SourceRead:
    source = await service.get(source_id)
    return SourceRead.model_validate(source)


@router.patch("/{source_id}", response_model=SourceRead)
async def update_source(
    source_id: int,
    payload: SourceUpdate,
    _user: User = Depends(require_operator_write),
    service: SourceService = Depends(get_source_service),
) -> SourceRead:
    source = await service.update(source_id, payload)
    return SourceRead.model_validate(source)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int,
    _user: User = Depends(require_operator_write),
    service: SourceService = Depends(get_source_service),
) -> None:
    await service.delete(source_id)
