import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.config import settings

JWT_ALGORITHM = "HS256"


def generate_secret_key(length: int = 64) -> str:
    return secrets.token_urlsafe(length)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    )
    return f"{salt}:{key.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    salt, key_hex = hashed.split(":")
    new_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    )
    return hmac.compare_digest(new_key.hex(), key_hex)


def create_access_token(
    data: dict[str, str | datetime],
    expires_delta: timedelta | None = None,
) -> dict[str, str | datetime]:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    return {
        **data,
        "exp": expire.isoformat(),
        "iat": datetime.now(UTC).isoformat(),
    }


def sign_jwt(
    claims: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> tuple[str, datetime]:
    expires_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    issued_at = datetime.now(UTC)
    payload = {
        **claims,
        "exp": expires_at,
        "iat": issued_at,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM), expires_at


def verify_jwt(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
