from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alert_event import AlertEvent
from app.models.article import Article
from app.models.intelligence_report import IntelligenceReport
from app.models.source import Source

CATEGORY_LABELS: dict[str, str] = {
    "wire": "通讯社/主流",
    "regional": "分地区媒体",
    "official": "政府/机构",
    "financial": "财经/宏观",
    "geopolitical": "地缘/OSINT",
    "cyber": "网络安全",
    "social": "社交/UGC",
    "research": "学术/研究",
    "vertical": "行业垂直",
    "aggregator": "聚合/API",
    "maritime": "海事/航空",
    "compliance": "制裁/合规",
    "humanitarian": "人道/灾害",
    "china": "大中华区",
    "thinktank": "智库/政策",
    "other": "其他",
}


def _effective_timestamp():
    return func.coalesce(Article.published_at, Article.created_at)


def archive_window_bounds(
    *,
    hours: int,
    timezone: str,
    now: datetime | None = None,
) -> tuple[datetime, datetime, datetime.date]:
    """Return (window_start, window_end, archive_date) using Beijing calendar day."""
    now = now or datetime.now(UTC)
    window_end = now
    window_start = now - timedelta(hours=hours)
    archive_date = now.astimezone(ZoneInfo(timezone)).date()
    return window_start, window_end, archive_date


def compute_heat_score(
    *,
    articles: int,
    high_relevance: int,
    avg_relevance: float,
) -> float:
    return round(articles + 3 * high_relevance + avg_relevance, 2)


def compute_daily_metrics(
    session: Session,
    *,
    window_start: datetime,
    window_end: datetime,
    min_relevance: float,
) -> dict[str, Any]:
    effective_ts = _effective_timestamp()
    base_filter = (effective_ts >= window_start) & (effective_ts <= window_end)

    articles_created = session.scalar(
        select(func.count()).select_from(Article).where(base_filter)
    ) or 0

    reports_created = session.scalar(
        select(func.count())
        .select_from(IntelligenceReport)
        .join(Article, Article.id == IntelligenceReport.article_id)
        .where(base_filter)
    ) or 0

    alert_events = session.scalar(
        select(func.count()).select_from(AlertEvent).where(AlertEvent.created_at >= window_start)
    ) or 0

    rows = session.execute(
        select(
            Source.category,
            Source.category_label,
            func.count(Article.id).label("articles"),
            func.count(IntelligenceReport.id).label("reports"),
            func.avg(IntelligenceReport.relevance_score).label("avg_rel"),
        )
        .select_from(Article)
        .join(Source, Source.id == Article.source_id)
        .outerjoin(IntelligenceReport, IntelligenceReport.article_id == Article.id)
        .where(base_filter)
        .group_by(Source.category, Source.category_label)
    ).all()

    high_rel_rows = session.execute(
        select(Source.category, func.count(IntelligenceReport.id))
        .select_from(Article)
        .join(Source, Source.id == Article.source_id)
        .join(IntelligenceReport, IntelligenceReport.article_id == Article.id)
        .where(base_filter)
        .where(IntelligenceReport.relevance_score >= min_relevance)
        .group_by(Source.category)
    ).all()
    high_by_cat = {cat: count for cat, count in high_rel_rows}

    by_source_type: dict[str, int] = defaultdict(int)
    st_rows = session.execute(
        select(Source.source_type, func.count(Article.id))
        .select_from(Article)
        .join(Source, Source.id == Article.source_id)
        .where(base_filter)
        .group_by(Source.source_type)
    ).all()
    for st, count in st_rows:
        by_source_type[st or "unknown"] = int(count)

    category_heat: list[dict[str, Any]] = []
    for category, label, art_count, rep_count, avg_rel in rows:
        cat = category or "other"
        articles = int(art_count or 0)
        reports = int(rep_count or 0)
        avg_relevance = round(float(avg_rel or 0.0), 2)
        high_relevance = int(high_by_cat.get(cat, 0))
        category_heat.append(
            {
                "category": cat,
                "category_label": label or CATEGORY_LABELS.get(cat, cat),
                "articles": articles,
                "reports": reports,
                "high_relevance": high_relevance,
                "avg_relevance": avg_relevance,
                "heat_score": compute_heat_score(
                    articles=articles,
                    high_relevance=high_relevance,
                    avg_relevance=avg_relevance,
                ),
            }
        )

    category_heat.sort(key=lambda row: row["heat_score"], reverse=True)

    avg_relevance_all = session.scalar(
        select(func.avg(IntelligenceReport.relevance_score))
        .select_from(IntelligenceReport)
        .join(Article, Article.id == IntelligenceReport.article_id)
        .where(base_filter)
    )

    high_relevance_all = session.scalar(
        select(func.count())
        .select_from(IntelligenceReport)
        .join(Article, Article.id == IntelligenceReport.article_id)
        .where(base_filter)
        .where(IntelligenceReport.relevance_score >= min_relevance)
    ) or 0

    return {
        "version": 1,
        "ingest": {
            "articles_created": int(articles_created),
            "by_source_type": dict(by_source_type),
        },
        "analysis": {
            "reports_created": int(reports_created),
            "avg_relevance": round(float(avg_relevance_all or 0.0), 2),
            "high_relevance_count": int(high_relevance_all),
        },
        "category_heat": category_heat,
        "alerts": {"events_created": int(alert_events)},
    }
