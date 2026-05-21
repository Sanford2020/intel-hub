from __future__ import annotations

from datetime import UTC, datetime

from app.config import settings
from app.modules.ingest.http_client import fetch_url
from app.modules.ingest.rss_parser import RssItem
from app.modules.ingest.social_items import clip_title, parse_iso_date

_MODE_PATHS: dict[str, str] = {
    "selected": "/api/public/items?limit=50",
    "all": "/api/public/items?limit=50&scope=all",
    "daily": "/api/public/items?limit=50&scope=daily",
}


def _normalize_mode(raw: str) -> str:
    value = raw.strip().lower()
    if value in _MODE_PATHS:
        return value
    if "scope=all" in value or value.endswith("/all"):
        return "all"
    if "scope=daily" in value or value.endswith("/daily"):
        return "daily"
    return "selected"


def _item_to_rss(row: dict) -> RssItem | None:
    title = (
        row.get("title")
        or row.get("name")
        or row.get("text")
        or row.get("summary")
        or ""
    ).strip()
    if not title:
        return None

    url = row.get("url") or row.get("link") or row.get("source_url")
    if not url and row.get("id") is not None:
        url = f"https://aihot.virxact.com/item/{row['id']}"

    published = parse_iso_date(
        row.get("published_at") or row.get("created_at") or row.get("date")
    )
    if published is None and row.get("timestamp"):
        try:
            published = datetime.fromtimestamp(float(row["timestamp"]), tz=UTC)
        except (TypeError, ValueError):
            published = None

    content = row.get("content") or row.get("description") or row.get("summary")
    author = row.get("author") or row.get("source") or row.get("platform")
    if author and content:
        content = f"[{author}] {content}"
    elif author:
        content = str(author)

    return RssItem(
        title=clip_title(title),
        url=str(url) if url else None,
        content=str(content) if content else None,
        published_at=published,
    )


def fetch_aihot_items(mode_or_url: str) -> list[RssItem]:
    """Fetch AI HOT public API items. `mode_or_url`: selected | all | daily."""
    mode = _normalize_mode(mode_or_url)
    base = settings.aihot_api_base.rstrip("/")
    path = _MODE_PATHS[mode]
    response = fetch_url(f"{base}{path}", timeout=25.0)
    data = response.json()

    rows: list[dict] = []
    if isinstance(data, list):
        rows = [r for r in data if isinstance(r, dict)]
    elif isinstance(data, dict):
        for key in ("items", "data", "results"):
            chunk = data.get(key)
            if isinstance(chunk, list):
                rows = [r for r in chunk if isinstance(r, dict)]
                break

    items: list[RssItem] = []
    for row in rows:
        item = _item_to_rss(row)
        if item and item.url:
            items.append(item)
    return items
