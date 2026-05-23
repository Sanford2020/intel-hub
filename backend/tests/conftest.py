import sys
import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
os.environ.setdefault("PROMPTS_DIR", str(_REPO_ROOT / "prompts"))

from app.api.deps import get_session
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.config import settings
from app.models import (  # noqa: F401
    AlertEvent,
    AlertRule,
    Article,
    BriefingDeliveryLog,
    DailyArchive,
    IntelligenceReport,
    Source,
    User,
    UserSession,
)

TEST_ADMIN_EMAIL = "admin@test.com"
TEST_ADMIN_PASSWORD = "test-password"


@pytest.fixture(autouse=True)
def _clear_bootstrap_admin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "initial_admin_email", "")
    monkeypatch.setattr(settings, "initial_admin_password", "")


@pytest.fixture
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        email=TEST_ADMIN_EMAIL,
        password_hash=hash_password(TEST_ADMIN_PASSWORD),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def _auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def unauthenticated_client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def client(
    db_session: AsyncSession,
    admin_user: User,
) -> Generator[TestClient, None, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        test_client.headers.update(
            _auth_headers(test_client, TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD)
        )
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def analyst_user(db_session: AsyncSession) -> User:
    user = User(
        email="analyst@test.com",
        password_hash=hash_password("analyst-password"),
        role="analyst",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def operator_user(db_session: AsyncSession) -> User:
    user = User(
        email="operator@test.com",
        password_hash=hash_password("operator-password"),
        role="operator",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def analyst_client(
    db_session: AsyncSession,
    analyst_user: User,
) -> Generator[TestClient, None, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        test_client.headers.update(
            _auth_headers(test_client, "analyst@test.com", "analyst-password")
        )
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def operator_client(
    db_session: AsyncSession,
    operator_user: User,
) -> Generator[TestClient, None, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        test_client.headers.update(
            _auth_headers(test_client, "operator@test.com", "operator-password")
        )
        yield test_client
    app.dependency_overrides.clear()
