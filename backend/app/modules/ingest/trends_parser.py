"""Parse public X/Google trend aggregator pages into ingest items."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from urllib.parse import unquote, urlparse

from app.modules.ingest.http_client import fetch_url
from app.modules.ingest.rss_parser import RssItem
from app.modules.ingest.social_items import clip_title

_MAX_ITEMS = 50
_TWITTER_SEARCH = re.compile(
    r'href="(https://twitter\.com/search\?q=([^"]+))"',
    re.IGNORECASE,
)
_GOOGLE_SEARCH = re.compile(
    r'href="(https://www\.google\.com/search\?q=([^"]+))"',
    re.IGNORECASE,
)
_GETDAYTRENDS_PATH = re.compile(r'href="(/trend/([^"]+)/)"', re.IGNORECASE)


def _topic_label(raw: str) -> str:
    text = unquote(raw).strip().strip('"')
    return text


def _format_rank_title(topic: str, rank: int, *, platform: str) -> str:
    label = topic if topic.startswith("#") else topic
    return clip_title(f"{label} ({platform} #{rank})")


def _append_unique(
    items: list[RssItem],
    seen: set[str],
    *,
    topic: str,
    url: str,
    content: str,
    platform: str,
) -> None:
    key = topic.casefold()
    if not topic or key in seen:
        return
    seen.add(key)
    rank = len(items) + 1
    items.append(
        RssItem(
            title=_format_rank_title(topic, rank, platform=platform),
            url=url,
            content=content,
            published_at=datetime.now(UTC),
        )
    )


def _parse_trends24(html: str) -> list[RssItem]:
    items: list[RssItem] = []
    seen: set[str] = set()
    for match in _TWITTER_SEARCH.finditer(html):
        url = match.group(1)
        topic = _topic_label(match.group(2))
        _append_unique(
            items,
            seen,
            topic=topic,
            url=url,
            content="X worldwide trending snapshot (trends24.in)",
            platform="X",
        )
        if len(items) >= _MAX_ITEMS:
            break
    return items


def _parse_getdaytrends(html: str, base_url: str) -> list[RssItem]:
    items: list[RssItem] = []
    seen: set[str] = set()
    origin = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
    for match in _GETDAYTRENDS_PATH.finditer(html):
        path = match.group(1)
        topic = _topic_label(match.group(2))
        url = f"{origin}{path}"
        _append_unique(
            items,
            seen,
            topic=topic,
            url=url,
            content="X trending snapshot (getdaytrends.com)",
            platform="X",
        )
        if len(items) >= _MAX_ITEMS:
            break
    return items


def _parse_trend_calendar(html: str, *, platform: str) -> list[RssItem]:
    items: list[RssItem] = []
    seen: set[str] = set()
    if platform == "google":
        pattern = _GOOGLE_SEARCH
        label = "Google"
        content = "Google India trending search snapshot (in.trend-calendar.com)"
    else:
        pattern = _TWITTER_SEARCH
        label = "X"
        content = "X India trending snapshot (in.trend-calendar.com)"

    for match in pattern.finditer(html):
        url = match.group(1)
        topic = _topic_label(match.group(2))
        _append_unique(
            items,
            seen,
            topic=topic,
            url=url,
            content=content,
            platform=label,
        )
        if len(items) >= _MAX_ITEMS:
            break
    return items


def _resolve_target(url: str) -> tuple[str, str]:
    """Return (fetch_url, platform_key). platform_key: trends24 | getdaytrends | calendar-x | calendar-google."""
    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "/").strip("/").lower()

    if "trends24.in" in host:
        return "https://trends24.in/", "trends24"
    if "getdaytrends.com" in host:
        return "https://getdaytrends.com/", "getdaytrends"
    if "trend-calendar.com" in host:
        if path in {"google", "google-trends"} or path.endswith("google"):
            return "https://in.trend-calendar.com/", "calendar-google"
        return "https://in.trend-calendar.com/", "calendar-x"

    raise ValueError(f"Unsupported trends URL: {url}")


def fetch_trends_items(url: str) -> list[RssItem]:
    """Fetch trending topics from trends24 / getdaytrends / trend-calendar."""
    fetch_target, platform = _resolve_target(url)
    response = fetch_url(fetch_target, timeout=30.0)
    html = response.text

    if platform == "trends24":
        items = _parse_trends24(html)
    elif platform == "getdaytrends":
        items = _parse_getdaytrends(html, fetch_target)
    elif platform == "calendar-google":
        items = _parse_trend_calendar(html, platform="google")
    else:
        items = _parse_trend_calendar(html, platform="x")

    if not items:
        raise ValueError(f"No trend topics parsed from {fetch_target} ({platform})")
    return items
