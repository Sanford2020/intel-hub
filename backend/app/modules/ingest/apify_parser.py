from __future__ import annotations

import re
from datetime import UTC, datetime

import httpx

from app.config import settings
from app.modules.ingest.http_client import resolve_http_proxy
from app.modules.ingest.rss_parser import RssItem
from app.modules.ingest.social_items import clip_title
from app.modules.ingest.x_parser import parse_x_username

_SEARCH_PREFIX = re.compile(r"^search:(.+)$", re.I)
_ACTOR_PREFIX = re.compile(r"^actor:(?P<actor>[^:]+):(?P<query>.+)$", re.I)


def _build_actor_input(query: str) -> dict:
    query = query.strip()
    search_match = _SEARCH_PREFIX.match(query)
    if search_match:
        return {
            "searchTerms": [search_match.group(1).strip()],
            "maxItems": 20,
        }
    handle = parse_x_username(query)
    return {
        "twitterHandles": [handle],
        "maxItems": 20,
    }


def _parse_actor_url(raw: str) -> tuple[str, str]:
    match = _ACTOR_PREFIX.match(raw.strip())
    if match:
        return match.group("actor"), match.group("query")
    return settings.apify_twitter_actor, raw


def _tweet_to_item(row: dict) -> RssItem | None:
    text = (row.get("text") or row.get("fullText") or row.get("tweetText") or "").strip()
    if not text:
        return None

    url = row.get("url") or row.get("twitterUrl")
    tweet_id = row.get("id") or row.get("tweetId")
    if not url and tweet_id:
        author = row.get("author") or {}
        username = author.get("userName") or author.get("username") or "i"
        url = f"https://x.com/{username}/status/{tweet_id}"

    created = row.get("createdAt") or row.get("created_at")
    published_at: datetime | None = None
    if created:
        try:
            published_at = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=UTC)
        except (TypeError, ValueError):
            published_at = None

    likes = row.get("likeCount") or row.get("likes")
    suffix = f" (♥{likes})" if likes is not None else ""
    return RssItem(
        title=clip_title(f"{text}{suffix}"),
        url=str(url) if url else None,
        content=text,
        published_at=published_at,
    )


def fetch_apify_items(source_url: str) -> list[RssItem]:
    """Run Apify Twitter actor synchronously and map dataset rows to articles."""
    token = settings.apify_token.strip()
    if not token:
        raise ValueError("APIFY_TOKEN is not configured")

    actor_id, query = _parse_actor_url(source_url)
    actor_path = actor_id.replace("/", "~")
    run_input = _build_actor_input(query)

    proxy = resolve_http_proxy()
    headers = {"Authorization": f"Bearer {token}"}
    base = "https://api.apify.com/v2"

    with httpx.Client(
        timeout=120.0,
        proxy=proxy,
        trust_env=True,
        verify=settings.http_ssl_verify,
    ) as client:
        run_resp = client.post(
            f"{base}/acts/{actor_path}/runs",
            params={"token": token, "waitForFinish": 120},
            json=run_input,
            headers=headers,
        )
        run_resp.raise_for_status()
        run_data = run_resp.json().get("data") or {}
        dataset_id = run_data.get("defaultDatasetId")
        if not dataset_id:
            raise ValueError("Apify run returned no defaultDatasetId")

        items_resp = client.get(
            f"{base}/datasets/{dataset_id}/items",
            params={"token": token, "limit": 50},
            headers=headers,
        )
        items_resp.raise_for_status()
        rows = items_resp.json()

    if not isinstance(rows, list):
        return []

    results: list[RssItem] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = _tweet_to_item(row)
        if item and item.url:
            results.append(item)
    return results
