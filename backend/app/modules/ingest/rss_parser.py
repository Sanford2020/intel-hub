from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

import feedparser


@dataclass(frozen=True)
class RssItem:
    title: str
    url: str | None
    content: str | None
    published_at: datetime | None


def _parse_published(entry: feedparser.FeedParserDict) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            return datetime(*parsed[:6], tzinfo=UTC)
    for key in ("published", "updated"):
        raw = entry.get(key)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=UTC)
                return dt
            except (TypeError, ValueError):
                continue
    return None


def _entry_content(entry: feedparser.FeedParserDict) -> str | None:
    if entry.get("summary"):
        return str(entry.summary)
    content_list = entry.get("content") or []
    if content_list:
        return str(content_list[0].get("value", "")) or None
    if entry.get("description"):
        return str(entry.description)
    return None


def parse_rss_feed(raw: str | bytes) -> list[RssItem]:
    parsed = feedparser.parse(raw)
    if getattr(parsed, "bozo", False) and not parsed.entries:
        exc = getattr(parsed, "bozo_exception", None)
        raise ValueError(f"Invalid RSS feed: {exc}")

    items: list[RssItem] = []
    for entry in parsed.entries:
        title = (entry.get("title") or "").strip()
        if not title:
            continue
        link = entry.get("link") or entry.get("id")
        url = str(link).strip() if link else None
        items.append(
            RssItem(
                title=title[:512],
                url=url[:2048] if url else None,
                content=_entry_content(entry),
                published_at=_parse_published(entry),
            )
        )
    return items


def fetch_rss_items(url: str, *, timeout: float = 20.0) -> list[RssItem]:
    from app.modules.ingest.http_client import fetch_url

    response = fetch_url(url, timeout=timeout)
    return parse_rss_feed(response.content)
