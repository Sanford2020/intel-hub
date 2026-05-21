from __future__ import annotations

import json
import re
import time
import urllib.parse
from datetime import UTC, datetime

import httpx

from app.config import settings
from app.modules.ingest.http_client import resolve_http_proxy
from app.modules.ingest.rss_parser import RssItem
from app.modules.ingest.social_items import clip_title, engagement_suffix

_REDDIT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

_SUB_RE = re.compile(r"^r/([\w_]+)$", re.I)
_SEARCH_RE = re.compile(r"^search:(.+)$", re.I)


def _reddit_json_url(path: str) -> str:
    base = f"https://www.reddit.com{path}"
    joiner = "&" if "?" in base else "?"
    return f"{base}{joiner}limit=15&raw_json=1"


def _parse_listing(data: dict) -> list[RssItem]:
    items: list[RssItem] = []
    for child in data.get("data", {}).get("children", []):
        if child.get("kind") != "t3":
            continue
        post = child.get("data", {})
        permalink = str(post.get("permalink") or "").strip()
        if not permalink:
            continue
        title = str(post.get("title") or "").strip()
        if not title:
            continue
        score = int(post.get("score") or 0)
        comments = int(post.get("num_comments") or 0)
        selftext = str(post.get("selftext") or "").strip()
        subreddit = str(post.get("subreddit") or "")
        author = str(post.get("author") or "")
        published_at: datetime | None = None
        created = post.get("created_utc")
        if created:
            try:
                published_at = datetime.fromtimestamp(float(created), tz=UTC)
            except (TypeError, ValueError, OSError):
                pass
        url = f"https://www.reddit.com{permalink}"
        body_parts = [f"r/{subreddit}" if subreddit else "", f"@{author}" if author else ""]
        if selftext:
            body_parts.append(selftext[:1500])
        content = "\n".join(p for p in body_parts if p) or None
        items.append(
            RssItem(
                title=clip_title(f"{title}{engagement_suffix({'score': score, 'num_comments': comments})}"),
                url=url,
                content=content,
                published_at=published_at,
            )
        )
    return items


def _fetch_with_backoff(url: str, *, retries: int = 3) -> dict:
    proxy = resolve_http_proxy()
    headers = {
        "User-Agent": _REDDIT_UA,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            with httpx.Client(
                timeout=25.0,
                follow_redirects=True,
                headers=headers,
                proxy=proxy,
                trust_env=True,
                verify=settings.http_ssl_verify,
            ) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(2.0 * (attempt + 1))
    raise ValueError(f"Reddit fetch failed: {last_exc}")


def fetch_reddit_items(spec: str) -> list[RssItem]:
    """Fetch Reddit posts from subreddit hot feed or search.

    URL formats:
    - r/worldnews — hot posts in subreddit
    - search:ukraine — global search (last month)
    - search:ukraine|r/geopolitics — scoped search
    """
    raw = spec.strip()
    scoped = raw.split("|", 1)
    main = scoped[0].strip()
    sub_override = scoped[1].strip() if len(scoped) > 1 else ""

    if sub_override:
        sub_match = _SUB_RE.match(sub_override)
        if not sub_match:
            raise ValueError(f"Invalid subreddit scope: {sub_override!r}")
        sub = sub_match.group(1)
        search_match = _SEARCH_RE.match(main)
        query = urllib.parse.quote_plus(
            search_match.group(1).strip() if search_match else main
        )
        path = (
            f"/r/{sub}/search.json?q={query}&restrict_sr=on"
            f"&sort=hot&t=month"
        )
        data = _fetch_with_backoff(_reddit_json_url(path))
        return _parse_listing(data)

    sub_match = _SUB_RE.match(main)
    if sub_match:
        sub = sub_match.group(1)
        data = _fetch_with_backoff(_reddit_json_url(f"/r/{sub}/hot.json"))
        return _parse_listing(data)

    search_match = _SEARCH_RE.match(main)
    query = search_match.group(1).strip() if search_match else main
    encoded = urllib.parse.quote_plus(query)
    data = _fetch_with_backoff(
        _reddit_json_url(f"/search.json?q={encoded}&sort=hot&t=month")
    )
    return _parse_listing(data)
