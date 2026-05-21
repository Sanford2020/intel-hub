from __future__ import annotations

import html
import re
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

from app.modules.ingest.http_client import fetch_url
from app.modules.ingest.rss_parser import RssItem
from app.modules.ingest.social_items import clip_title, engagement_suffix

ALGOLIA_SEARCH = "https://hn.algolia.com/api/v1/search_by_date"
_HN_PREFIX = re.compile(r"^(Tell HN|Show HN|Ask HN|Launch HN)\s*:\s*", re.I)


def _topic(spec: str) -> str:
    raw = spec.strip()
    if raw.lower().startswith("search:"):
        return raw[7:].strip()
    return raw


def fetch_hn_items(spec: str) -> list[RssItem]:
    """Search Hacker News via Algolia (free, last ~30 days)."""
    query = _topic(spec)
    if not query:
        raise ValueError("HN source URL/query is empty")

    since = datetime.now(UTC) - timedelta(days=30)
    params = {
        "query": query.replace(",", " ").replace("-", " "),
        "tags": "story",
        "numericFilters": f"created_at_i>{int(since.timestamp())},points>2",
        "hitsPerPage": "30",
    }
    tokens = params["query"].split()
    if len(tokens) > 1:
        params["optionalWords"] = " ".join(tokens[1:])

    url = f"{ALGOLIA_SEARCH}?{urlencode(params)}"
    response = fetch_url(url, timeout=30.0)
    data = response.json()
    items: list[RssItem] = []

    for hit in data.get("hits", []):
        title = _HN_PREFIX.sub("", str(hit.get("title") or "")).strip()
        if not title:
            continue
        object_id = hit.get("objectID", "")
        points = int(hit.get("points") or 0)
        comments = int(hit.get("num_comments") or 0)
        article_url = str(hit.get("url") or "").strip()
        hn_url = f"https://news.ycombinator.com/item?id={object_id}"
        url = article_url or hn_url
        published_at: datetime | None = None
        created_i = hit.get("created_at_i")
        if created_i:
            try:
                published_at = datetime.fromtimestamp(int(created_i), tz=UTC)
            except (TypeError, ValueError, OSError):
                pass
        author = str(hit.get("author") or "")
        content = f"HN discussion: {hn_url}"
        if author:
            content = f"@{author}\n{content}"
        items.append(
            RssItem(
                title=clip_title(
                    f"{title}{engagement_suffix({'points': points, 'comments': comments})}"
                ),
                url=url,
                content=content,
                published_at=published_at,
            )
        )
    return items
