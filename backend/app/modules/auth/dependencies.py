from typing import Annotated, Any

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.errors import AuthenticationError, PermissionDeniedError
from app.core.security import verify_jwt
from app.models.user import User
from app.modules.auth.service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    service: AuthService = Depends(get_auth_service),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError(message="Missing bearer token")
    try:
        payload: dict[str, Any] = verify_jwt(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise AuthenticationError(message="Invalid or expired token") from exc

    jti = payload.get("jti")
    if not isinstance(jti, str) or not jti:
        raise AuthenticationError(message="Invalid or expired token")
    session = await service.get_active_session(jti)
    return session.user


async def get_current_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError(message="Missing bearer token")
    try:
        return verify_jwt(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise AuthenticationError(message="Invalid or expired token") from exc


def require_roles(*roles: str):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise PermissionDeniedError(message="Permission denied")
        return user

    return dependency


require_admin = require_roles("admin")
require_operator_write = require_roles("admin", "operator")
