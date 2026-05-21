from __future__ import annotations

from datetime import UTC, datetime

from app.modules.ingest.rss_parser import RssItem


def clip_title(text: str, limit: int = 200) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 1]}…"


def parse_iso_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        if len(value) == 10 and value[4] == "-":
            return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def engagement_suffix(meta: dict[str, int | str | None]) -> str:
    parts: list[str] = []
    for key, label in (
        ("score", "↑"),
        ("points", "pts"),
        ("likes", "♥"),
        ("comments", "💬"),
        ("num_comments", "💬"),
    ):
        val = meta.get(key)
        if val is not None and val != "":
            parts.append(f"{label}{val}")
    return f" ({', '.join(parts)})" if parts else ""
