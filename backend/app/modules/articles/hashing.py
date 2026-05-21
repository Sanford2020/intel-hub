import hashlib


def article_content_hash(title: str, url: str | None = None) -> str:
    normalized_url = (url or "").strip().lower()
    normalized_title = title.strip().lower()
    payload = normalized_url if normalized_url else f"{normalized_title}|{normalized_url}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
