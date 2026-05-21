import hashlib
import re
import uuid
from datetime import UTC, datetime


def generate_id() -> str:
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    return uuid.uuid4().hex[:length]


def now_utc() -> datetime:
    return datetime.now(UTC)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def hash_string(value: str, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    h.update(value.encode("utf-8"))
    return h.hexdigest()


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def chunk_list(lst: list, chunk_size: int) -> list[list]:  # type: ignore[type-arg]
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
