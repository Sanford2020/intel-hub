from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.errors import ConflictError, NotFoundError
from app.models.ingest_log import IngestLog
from app.models.source import Source
from app.modules.sources.schemas import (
    SourceBulkImportRequest,
    SourceBulkImportResult,
    SourceCreate,
    SourceSeedImport,
    SourceUpdate,
)


def _interval_for_tier(tier: int) -> int:
    if tier == 0:
        return 15
    if tier == 1:
        return 30
    return settings.ingest_default_interval_minutes


def _source_from_seed(row: SourceSeedImport) -> Source:
    return Source(
        name=row.name,
        slug=row.slug,
        category=row.category,
        category_label=row.category_label,
        subcategory=row.subcategory,
        section=row.section,
        source_type=row.type,
        url=row.url,
        language=row.language,
        region=row.region,
        tier=row.tier,
        enabled=row.enabled,
        fetch_interval_minutes=_interval_for_tier(row.tier),
        api_key_env=row.api_key_env,
        license_notes=row.license_notes,
        source_file=row.source_file,
    )


class SourceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: SourceCreate) -> Source:
        existing = await self.session.scalar(
            select(Source).where(Source.slug == payload.slug)
        )
        if existing:
            raise ConflictError(
                message=f"Source slug already exists: {payload.slug}",
                details={"slug": payload.slug},
            )
        source = Source(**payload.model_dump())
        self.session.add(source)
        await self.session.flush()
        await self.session.refresh(source)
        return source

    async def get(self, source_id: int) -> Source:
        source = await self.session.get(Source, source_id)
        if not source:
            raise NotFoundError(message=f"Source {source_id} not found")
        return source

    async def get_by_slug(self, slug: str) -> Source:
        source = await self.session.scalar(select(Source).where(Source.slug == slug))
        if not source:
            raise NotFoundError(message=f"Source slug not found: {slug}")
        return source

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        category: str | None = None,
        tier: int | None = None,
        enabled: bool | None = None,
    ) -> tuple[list[Source], int]:
        query = select(Source)
        if category:
            query = query.where(Source.category == category)
        if tier is not None:
            query = query.where(Source.tier == tier)
        if enabled is not None:
            query = query.where(Source.enabled == enabled)

        count_query = select(func.count()).select_from(query.subquery())
        total = int(await self.session.scalar(count_query) or 0)

        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size
        rows = await self.session.scalars(
            query.order_by(Source.tier, Source.name).offset(offset).limit(page_size)
        )
        return list(rows.all()), total

    async def update(self, source_id: int, payload: SourceUpdate) -> Source:
        source = await self.get(source_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(source, key, value)
        await self.session.flush()
        await self.session.refresh(source)
        return source

    async def delete(self, source_id: int) -> None:
        source = await self.get(source_id)
        await self.session.delete(source)

    async def bulk_import(self, payload: SourceBulkImportRequest) -> SourceBulkImportResult:
        created = skipped = updated = 0
        for row in payload.sources:
            existing = await self.session.scalar(
                select(Source).where(Source.slug == row.slug)
            )
            if existing:
                if payload.skip_existing:
                    skipped += 1
                    continue
                for key, value in row.model_dump().items():
                    if key == "type":
                        setattr(existing, "source_type", value)
                    elif key != "slug":
                        setattr(existing, key, value)
                existing.fetch_interval_minutes = _interval_for_tier(row.tier)
                updated += 1
                continue
            self.session.add(_source_from_seed(row))
            created += 1
        await self.session.flush()
        return SourceBulkImportResult(
            created=created,
            skipped=skipped,
            updated=updated,
        )

    async def list_ingest_logs(
        self,
        source_id: int,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[IngestLog], int]:
        await self.get(source_id)
        query = select(IngestLog).where(IngestLog.source_id == source_id)
        count_query = select(func.count()).select_from(query.subquery())
        total = int(await self.session.scalar(count_query) or 0)

        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size
        rows = await self.session.scalars(
            query.order_by(IngestLog.id.desc()).offset(offset).limit(page_size)
        )
        return list(rows.all()), total
