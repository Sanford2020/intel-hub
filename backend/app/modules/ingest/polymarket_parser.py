from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import urlencode

from app.modules.ingest.http_client import fetch_url
from app.modules.ingest.rss_parser import RssItem
from app.modules.ingest.social_items import clip_title

GAMMA_SEARCH = "https://gamma-api.polymarket.com/public-search"


def _topic(spec: str) -> str:
    raw = spec.strip()
    if raw.lower().startswith("search:"):
        return raw[7:].strip()
    return raw


def fetch_polymarket_items(spec: str) -> list[RssItem]:
    """Fetch active Polymarket events via Gamma API (free)."""
    query = _topic(spec)
    if not query:
        raise ValueError("Polymarket search query is empty")

    params = urlencode(
        {
            "q": query,
            "page": "1",
            "events_status": "active",
            "keep_closed_markets": "0",
        }
    )
    response = fetch_url(f"{GAMMA_SEARCH}?{params}", timeout=25.0)
    data = response.json()
    events = data.get("events") or data.get("data") or []
    if isinstance(data, list):
        events = data

    items: list[RssItem] = []
    seen: set[str] = set()

    for event in events[:20]:
        if not isinstance(event, dict):
            continue
        title = str(event.get("title") or event.get("question") or "").strip()
        if not title or title in seen:
            continue
        seen.add(title)

        slug = str(event.get("slug") or event.get("id") or "").strip()
        url = f"https://polymarket.com/event/{slug}" if slug else "https://polymarket.com"
        markets = event.get("markets") or []
        odds_lines: list[str] = []
        for market in markets[:3]:
            if not isinstance(market, dict):
                continue
            q = str(market.get("question") or market.get("groupItemTitle") or "").strip()
            outcome_prices = market.get("outcomePrices") or market.get("outcome_prices")
            if q and outcome_prices:
                odds_lines.append(f"{q}: {outcome_prices}")
        volume = event.get("volume") or event.get("volume24hr")
        content_parts = odds_lines[:5]
        if volume:
            content_parts.append(f"Volume: {volume}")
        content = "\n".join(content_parts) or None

        items.append(
            RssItem(
                title=clip_title(f"[Polymarket] {title}"),
                url=url,
                content=content,
                published_at=datetime.now(UTC),
            )
        )

    return items
