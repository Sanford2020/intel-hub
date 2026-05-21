from __future__ import annotations

from collections import Counter
from datetime import datetime

from app.modules.briefings.aggregator import BriefingRow
from app.modules.briefings.schemas import BriefingItemRead, BriefingMetaRead, DailyBriefingRead


def detect_ai_mode(items: list[BriefingItemRead]) -> str:
    if any(item.model and "mock" in item.model.lower() for item in items):
        return "mock"
    return "live"


def build_overview(items: list[BriefingItemRead], *, ai_mode: str) -> str:
    count = len(items)
    if count == 0:
        return "过去时间窗内暂无已分析的资讯。请先采集来源并运行 AI 分析。"

    tag_counts: Counter[str] = Counter()
    for item in items:
        tag_counts.update(item.tags)

    top_tags = [tag for tag, _ in tag_counts.most_common(3)]
    tag_part = f"主要主题：{', '.join(top_tags)}" if top_tags else "主题分布较分散"

    mode_note = "（当前为 Mock AI 分析模式）" if ai_mode == "mock" else ""
    return f"过去时间窗内共 {count} 条高相关情报，{tag_part}。{mode_note}".strip()


def rows_to_items(rows: list[BriefingRow]) -> list[BriefingItemRead]:
    items: list[BriefingItemRead] = []
    for rank, row in enumerate(rows, start=1):
        report = row.report
        items.append(
            BriefingItemRead(
                rank=rank,
                article_id=row.article.id,
                source_id=row.article.source_id,
                source_name=row.source_name,
                title=row.article.title,
                url=row.article.url,
                published_at=row.article.published_at,
                summary=report.summary,
                tags=report.tags or [],
                relevance_score=report.relevance_score,
                sentiment=report.sentiment,
                model=report.model,
            )
        )
    return items


def to_markdown(briefing: DailyBriefingRead) -> str:
    meta = briefing.meta
    lines = [
        "# Intel Hub 每日简报",
        "",
        f"- 生成时间：{meta.generated_at.isoformat()}",
        f"- 时间窗：{meta.window_start.isoformat()} → {meta.window_end.isoformat()}",
        f"- 条目数：{meta.item_count}",
        "",
        briefing.overview,
        "",
    ]
    if not briefing.items:
        lines.append("_暂无条目_")
        return "\n".join(lines)

    for item in briefing.items:
        lines.extend(
            [
                f"## {item.rank}. {item.title}",
                "",
                f"- 来源：{item.source_name}",
                f"- 相关度：{item.relevance_score:.1f}",
                f"- 标签：{', '.join(item.tags) if item.tags else '—'}",
            ]
        )
        if item.url:
            lines.append(f"- 链接：{item.url}")
        lines.extend(["", item.summary, ""])

    return "\n".join(lines).rstrip() + "\n"


def assemble_daily_briefing(
    rows: list[BriefingRow],
    *,
    window_hours: int,
    window_start: datetime,
    window_end: datetime,
    limit: int,
    min_relevance: float | None,
    include_markdown: bool = False,
) -> DailyBriefingRead:
    items = rows_to_items(rows)
    ai_mode = detect_ai_mode(items)
    overview = build_overview(items, ai_mode=ai_mode)
    meta = BriefingMetaRead(
        generated_at=window_end,
        window_hours=window_hours,
        window_start=window_start,
        window_end=window_end,
        item_count=len(items),
        limit=limit,
        min_relevance=min_relevance,
        ai_mode=ai_mode,
    )
    briefing = DailyBriefingRead(meta=meta, overview=overview, items=items)
    if include_markdown:
        briefing.markdown = to_markdown(briefing)
    return briefing
