from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.config import settings
from app.modules.ingest.rss_parser import RssItem
from app.modules.ingest.social_items import clip_title, engagement_suffix

_BIRD_MJS = (
    Path(__file__).resolve().parent / "vendor" / "bird-search" / "bird-search.mjs"
)


def bird_available() -> bool:
    return _BIRD_MJS.is_file() and shutil.which("node") is not None


def _bird_credentials() -> tuple[str, str]:
    auth = settings.x_auth_token or os.environ.get("AUTH_TOKEN", "")
    ct0 = settings.x_ct0 or os.environ.get("CT0", "")
    return auth.strip(), ct0.strip()


def bird_authenticated() -> bool:
    auth, ct0 = _bird_credentials()
    return bool(auth and ct0)


def _bird_env() -> dict[str, str]:
    env = os.environ.copy()
    auth, ct0 = _bird_credentials()
    if auth:
        env["AUTH_TOKEN"] = auth
    if ct0:
        env["CT0"] = ct0
    env["BIRD_DISABLE_BROWSER_COOKIES"] = "1"
    return env


def _parse_tweets(raw: list | dict) -> list[RssItem]:
    tweets = raw if isinstance(raw, list) else raw.get("items") or raw.get("tweets") or []
    items: list[RssItem] = []
    for tweet in tweets:
        if not isinstance(tweet, dict):
            continue
        text = str(tweet.get("text") or tweet.get("full_text") or "").strip()
        if not text:
            continue
        author = tweet.get("author") or tweet.get("user") or {}
        handle = (
            author.get("username")
            or author.get("screen_name")
            or tweet.get("author_handle")
            or ""
        )
        tweet_id = tweet.get("id")
        url = tweet.get("permanent_url") or tweet.get("url") or ""
        if not url and handle and tweet_id:
            url = f"https://x.com/{handle.lstrip('@')}/status/{tweet_id}"
        if not url:
            continue

        published_at: datetime | None = None
        created = tweet.get("createdAt") or tweet.get("created_at")
        if created:
            try:
                if isinstance(created, str) and len(created) > 10 and created[10] == "T":
                    published_at = datetime.fromisoformat(created.replace("Z", "+00:00"))
                else:
                    published_at = datetime.strptime(
                        str(created), "%a %b %d %H:%M:%S %z %Y"
                    )
            except (TypeError, ValueError):
                pass

        likes = tweet.get("likeCount") or tweet.get("favorite_count")
        reposts = tweet.get("retweetCount") or tweet.get("retweet_count")
        meta: dict[str, int | str | None] = {}
        if likes is not None:
            meta["likes"] = likes
        if reposts is not None:
            meta["score"] = reposts

        prefix = f"@{handle.lstrip('@')}: " if handle else ""
        items.append(
            RssItem(
                title=clip_title(f"{prefix}{text}{engagement_suffix(meta)}"),
                url=url,
                content=text,
                published_at=published_at,
            )
        )
    return items


def _run_bird_search(query: str, *, count: int = 25, timeout: int = 45) -> list[RssItem]:
    if not bird_available():
        raise ValueError("Node.js or vendored bird-search is not available")
    if not bird_authenticated():
        raise ValueError(
            "X session cookies missing — set X_AUTH_TOKEN and X_CT0 in backend/.env "
            "(from x.com cookies auth_token and ct0)"
        )

    cmd = [
        "node",
        str(_BIRD_MJS),
        query,
        "--count",
        str(count),
        "--json",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=_bird_env(),
        check=False,
    )
    stdout = (result.stdout or "").strip()
    if not stdout:
        err = (result.stderr or "").strip() or f"exit code {result.returncode}"
        raise ValueError(f"Bird search failed: {err}")

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Bird returned non-JSON: {exc}") from exc

    if isinstance(payload, dict) and payload.get("error"):
        raise ValueError(str(payload["error"]))

    return _parse_tweets(payload)


def fetch_x_bird_handle(handle: str, *, count: int = 20) -> list[RssItem]:
    user = handle.lstrip("@")
    since = (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d")
    return _run_bird_search(f"from:{user} since:{since}", count=count)


def fetch_x_bird_search(query: str, *, count: int = 25) -> list[RssItem]:
    since = (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d")
    core = query.strip()
    return _run_bird_search(f"{core} since:{since}", count=count)
