from __future__ import annotations

import re
from datetime import datetime

from app.config import settings
from app.modules.ingest.bird_parser import (
    bird_authenticated,
    bird_available,
    fetch_x_bird_handle,
    fetch_x_bird_search,
)
from app.modules.ingest.rss_parser import RssItem, fetch_rss_items

_X_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:twitter|x)\.com/(?P<user>[A-Za-z0-9_]{1,15})(?:/|$|\?)",
    re.I,
)
_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{1,15}$")
_SEARCH_PREFIX = re.compile(r"^search:(.+)$", re.I)


def parse_x_username(raw: str) -> str:
    """Extract X handle from @user, bare handle, or profile URL."""
    value = raw.strip()
    if not value:
        raise ValueError("Empty X handle")
    if value.startswith("@"):
        value = value[1:]
    match = _X_URL_RE.match(value)
    if match:
        return match.group("user")
    if _USERNAME_RE.fullmatch(value):
        return value
    raise ValueError(f"Cannot parse X username from: {raw!r}")


def _fetch_x_via_api(username: str, bearer_token: str) -> list[RssItem]:
    import httpx

    from app.modules.ingest.http_client import resolve_http_proxy

    headers = {"Authorization": f"Bearer {bearer_token}"}
    base = "https://api.twitter.com/2"
    proxy = resolve_http_proxy()
    with httpx.Client(timeout=20.0, proxy=proxy, trust_env=True) as client:
        user_resp = client.get(
            f"{base}/users/by/username/{username}",
            headers=headers,
        )
        user_resp.raise_for_status()
        user_id = user_resp.json()["data"]["id"]
        tweets_resp = client.get(
            f"{base}/users/{user_id}/tweets",
            headers=headers,
            params={
                "max_results": 20,
                "tweet.fields": "created_at,text",
                "exclude": "retweets,replies",
            },
        )
        tweets_resp.raise_for_status()

    items: list[RssItem] = []
    for tweet in tweets_resp.json().get("data") or []:
        text = str(tweet.get("text") or "").strip()
        if not text:
            continue
        tweet_id = tweet["id"]
        url = f"https://x.com/{username}/status/{tweet_id}"
        published_at: datetime | None = None
        created_at = tweet.get("created_at")
        if created_at:
            published_at = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
        title = text if len(text) <= 200 else f"{text[:197]}…"
        items.append(
            RssItem(
                title=title,
                url=url,
                content=text,
                published_at=published_at,
            )
        )
    return items


_BRIDGE_ERROR_MARKERS = ("rss reader not yet whitelisted", "not yet whitelisted")


def _bridge_error(items: list[RssItem]) -> str | None:
    if not items:
        return "empty feed"
    if len(items) == 1:
        title = (items[0].title or "").strip().lower()
        for marker in _BRIDGE_ERROR_MARKERS:
            if marker in title:
                return items[0].title
    return None


def _fetch_x_via_rss_bridge(username: str) -> list[RssItem]:
    bridge_bases = [
        settings.x_rss_bridge_base.rstrip("/"),
        "https://rss.xcancel.com",
        "https://xcancel.com",
    ]
    seen: set[str] = set()
    errors: list[str] = []
    for base in bridge_bases:
        if not base or base in seen:
            continue
        seen.add(base)
        rss_url = f"{base}/{username}/rss"
        try:
            items = fetch_rss_items(rss_url, timeout=30.0)
            bridge_err = _bridge_error(items)
            if bridge_err:
                errors.append(f"{rss_url}: {bridge_err}")
                continue
            if items:
                return items
            errors.append(f"{rss_url}: empty feed")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rss_url}: {exc}")
    raise ValueError("; ".join(errors))


def fetch_x_items(url: str) -> list[RssItem]:
    """Fetch X content: search query, user timeline, API, Bird cookies, or RSS bridge."""
    raw = url.strip()
    search_match = _SEARCH_PREFIX.match(raw)
    if search_match:
        query = search_match.group(1).strip()
        if settings.x_bearer_token:
            raise ValueError("X search queries require Bird cookies (X_AUTH_TOKEN/X_CT0)")
        if bird_available() and bird_authenticated():
            return fetch_x_bird_search(query)
        raise ValueError(
            "X search requires Bird session cookies — set X_AUTH_TOKEN and X_CT0 in backend/.env"
        )

    username = parse_x_username(raw)
    errors: list[str] = []

    if settings.x_bearer_token:
        try:
            return _fetch_x_via_api(username, settings.x_bearer_token)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"API: {exc}")

    if bird_available() and bird_authenticated():
        try:
            return fetch_x_bird_handle(username)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Bird: {exc}")

    try:
        return _fetch_x_via_rss_bridge(username)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"RSS bridge: {exc}")

    hint = (
        "Set X_AUTH_TOKEN + X_CT0 (x.com cookies) for Bird search, "
        "or X_BEARER_TOKEN for official API."
    )
    raise ValueError(f"All X fetch methods failed ({'; '.join(errors)}). {hint}")
