from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from time import perf_counter
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.ingest_log import IngestLog
from app.models.source import Source
from app.modules.articles.hashing import article_content_hash
from app.modules.ingest.hn_parser import fetch_hn_items
from app.modules.ingest.polymarket_parser import fetch_polymarket_items
from app.modules.ingest.reddit_parser import fetch_reddit_items
from app.modules.ingest.rss_parser import RssItem, fetch_rss_items
from app.modules.ingest.x_parser import fetch_x_items
from app.modules.ingest.aihot_parser import fetch_aihot_items
from app.modules.ingest.apify_parser import fetch_apify_items
from app.modules.ingest.trends_parser import fetch_trends_items

INGESTIBLE_SOURCE_TYPES = frozenset(
    {"rss", "x", "reddit", "hn", "polymarket", "aihot", "apify", "trends"}
)


@dataclass
class IngestResult:
    source_id: int
    status: str
    items_found: int = 0
    items_created: int = 0
    items_skipped: int = 0
    created_article_ids: list[int] | None = None
    error_message: str | None = None
    duration_ms: int | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        if data["created_article_ids"] is None:
            data["created_article_ids"] = []
        return data


def source_is_due(source: Source, now: datetime | None = None) -> bool:
    now = now or datetime.now(UTC)
    if not source.enabled or source.source_type not in INGESTIBLE_SOURCE_TYPES or not source.url:
        return False
    if source.last_ingested_at is None:
        return True
    elapsed = (now - source.last_ingested_at).total_seconds()
    return elapsed >= source.fetch_interval_minutes * 60


def list_due_rss_source_ids(session: Session) -> list[int]:
    """Backward-compatible alias for scheduled RSS + X ingest."""
    return list_due_source_ids(session)


def list_due_source_ids(session: Session) -> list[int]:
    now = datetime.now(UTC)
    sources = session.scalars(
        select(Source).where(
            Source.enabled.is_(True),
            Source.source_type.in_(INGESTIBLE_SOURCE_TYPES),
            Source.url.isnot(None),
        )
    )
    return [source.id for source in sources.all() if source_is_due(source, now)]


def _persist_items(
    session: Session,
    source: Source,
    items: list[RssItem],
) -> tuple[int, int, list[int]]:
    created = skipped = 0
    new_ids: list[int] = []
    for item in items:
        content_hash = article_content_hash(item.title, item.url)
        exists = session.scalar(
            select(Article.id).where(Article.content_hash == content_hash)
        )
        if exists:
            skipped += 1
            continue
        article = Article(
            source_id=source.id,
            title=item.title,
            url=item.url,
            content=item.content,
            content_hash=content_hash,
            published_at=item.published_at,
            language=source.language,
        )
        session.add(article)
        session.flush()
        new_ids.append(article.id)
        created += 1
    return created, skipped, new_ids


def _skip_reason(source: Source) -> str:
    reasons: list[str] = []
    if not source.enabled:
        reasons.append("来源未启用")
    if source.source_type not in INGESTIBLE_SOURCE_TYPES:
        reasons.append(
            f"来源类型为 {source.source_type}，仅支持 {', '.join(sorted(INGESTIBLE_SOURCE_TYPES))}"
        )
    if not source.url:
        reasons.append("未配置 URL / 账号")
    return "；".join(reasons)


def _record_ingest_log(
    session: Session,
    *,
    source_id: int,
    status: str,
    started: float,
    error_message: str | None = None,
    items_found: int = 0,
    items_created: int = 0,
    items_skipped: int = 0,
) -> IngestLog:
    duration_ms = int((perf_counter() - started) * 1000)
    log = IngestLog(
        source_id=source_id,
        status=status,
        items_found=items_found,
        items_created=items_created,
        items_skipped=items_skipped,
        error_message=error_message,
        duration_ms=duration_ms,
        finished_at=datetime.now(UTC),
    )
    session.add(log)
    session.flush()
    return log


def _fetch_items_for_source(source: Source) -> list[RssItem]:
    url = source.url or ""
    if source.source_type == "rss":
        return fetch_rss_items(url)
    if source.source_type == "x":
        return fetch_x_items(url)
    if source.source_type == "reddit":
        return fetch_reddit_items(url)
    if source.source_type == "hn":
        return fetch_hn_items(url)
    if source.source_type == "polymarket":
        return fetch_polymarket_items(url)
    if source.source_type == "aihot":
        return fetch_aihot_items(url)
    if source.source_type == "apify":
        return fetch_apify_items(url)
    if source.source_type == "trends":
        return fetch_trends_items(url)
    raise ValueError(f"Unsupported source type: {source.source_type}")


def _ingest_source_with_fetcher(
    session: Session,
    source_id: int,
    fetch_items: Callable[[Source], list[RssItem]],
) -> IngestResult:
    started = perf_counter()
    source = session.get(Source, source_id)
    if not source:
        return IngestResult(source_id=source_id, status="not_found")
    if (
        not source.enabled
        or source.source_type not in INGESTIBLE_SOURCE_TYPES
        or not source.url
    ):
        message = _skip_reason(source)
        duration_ms = int((perf_counter() - started) * 1000)
        _record_ingest_log(
            session,
            source_id=source.id,
            status="skipped",
            started=started,
            error_message=message,
        )
        return IngestResult(
            source_id=source_id,
            status="skipped",
            error_message=message,
            duration_ms=duration_ms,
        )

    log = IngestLog(
        source_id=source.id,
        status="running",
        items_found=0,
        items_created=0,
        items_skipped=0,
    )
    session.add(log)
    session.flush()

    try:
        items = fetch_items(source)
        created, skipped, new_ids = _persist_items(session, source, items)
        source.last_ingested_at = datetime.now(UTC)
        duration_ms = int((perf_counter() - started) * 1000)
        log.status = "success"
        log.items_found = len(items)
        log.items_created = created
        log.items_skipped = skipped
        log.duration_ms = duration_ms
        log.finished_at = datetime.now(UTC)
        session.flush()
        return IngestResult(
            source_id=source_id,
            status="success",
            items_found=len(items),
            items_created=created,
            items_skipped=skipped,
            created_article_ids=new_ids,
            duration_ms=duration_ms,
        )
    except Exception as exc:  # noqa: BLE001
        duration_ms = int((perf_counter() - started) * 1000)
        log.status = "failed"
        log.error_message = str(exc)[:2000]
        log.duration_ms = duration_ms
        log.finished_at = datetime.now(UTC)
        session.flush()
        return IngestResult(
            source_id=source_id,
            status="failed",
            error_message=str(exc),
            duration_ms=duration_ms,
        )


def ingest_source(session: Session, source_id: int) -> IngestResult:
    return _ingest_source_with_fetcher(session, source_id, _fetch_items_for_source)


def ingest_rss_source(session: Session, source_id: int) -> IngestResult:
    """Backward-compatible RSS-only entry (delegates to unified ingest)."""
    return ingest_source(session, source_id)
