from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.errors import AuthenticationError, ConflictError
from app.core.security import hash_password, sign_jwt, verify_password
from app.models.user import User, UserSession


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bootstrap_initial_admin(self) -> None:
        if not settings.initial_admin_email or not settings.initial_admin_password:
            return
        existing = await self.session.scalar(
            select(User).where(User.email == settings.initial_admin_email.lower())
        )
        if existing:
            return
        self.session.add(
            User(
                email=settings.initial_admin_email.lower(),
                password_hash=hash_password(settings.initial_admin_password),
                role="admin",
                is_active=True,
            )
        )
        await self.session.flush()

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> tuple[User, str, datetime]:
        await self.bootstrap_initial_admin()
        user = await self.session.scalar(
            select(User)
            .options(selectinload(User.sessions))
            .where(User.email == email.lower())
        )
        if (
            not user
            or not user.is_active
            or not verify_password(password, user.password_hash)
        ):
            raise AuthenticationError(message="Invalid email or password")

        jti = uuid4().hex
        token, expires_at = sign_jwt(
            {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
                "jti": jti,
            }
        )
        self.session.add(UserSession(user_id=user.id, jti=jti, expires_at=expires_at))
        await self.session.flush()
        await self.session.refresh(user)
        return user, token, expires_at

    async def get_active_session(self, jti: str) -> UserSession:
        session = await self.session.scalar(
            select(UserSession)
            .options(selectinload(UserSession.user))
            .where(UserSession.jti == jti)
        )
        if not session or session.revoked_at is not None:
            raise AuthenticationError(message="Invalid or expired token")
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= datetime.now(UTC):
            raise AuthenticationError(message="Invalid or expired token")
        if not session.user.is_active:
            raise AuthenticationError(message="User is inactive")
        return session

    async def revoke_session(self, jti: str) -> None:
        session = await self.get_active_session(jti)
        session.revoked_at = datetime.now(UTC)
        await self.session.flush()

    async def create_user(self, email: str, password: str, role: str) -> User:
        normalized = email.lower()
        existing = await self.session.scalar(select(User).where(User.email == normalized))
        if existing:
            raise ConflictError(message="User already exists")
        user = User(
            email=normalized,
            password_hash=hash_password(password),
            role=role,
            is_active=True,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
