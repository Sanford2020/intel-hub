from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.config import settings
from app.models.user import User


async def test_login_returns_jwt_and_me_returns_user(
    unauthenticated_client: TestClient,
    db_session,
) -> None:
    db_session.add(
        User(
            email="admin@example.com",
            password_hash=hash_password("correct-password"),
            role="admin",
            is_active=True,
        )
    )
    await db_session.commit()

    login = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "correct-password"},
    )

    assert login.status_code == 200
    body = login.json()
    assert body["token_type"] == "bearer"  # noqa: S105
    assert body["access_token"]
    assert body["user"]["email"] == "admin@example.com"
    assert body["user"]["role"] == "admin"

    me = unauthenticated_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "admin@example.com"


async def test_login_rejects_wrong_password(unauthenticated_client: TestClient, db_session) -> None:
    db_session.add(
        User(
            email="admin@example.com",
            password_hash=hash_password("correct-password"),
            role="admin",
            is_active=True,
        )
    )
    await db_session.commit()

    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


async def test_logout_revokes_session_token(unauthenticated_client: TestClient, db_session) -> None:
    db_session.add(
        User(
            email="admin@example.com",
            password_hash=hash_password("correct-password"),
            role="admin",
            is_active=True,
        )
    )
    await db_session.commit()

    login = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "correct-password"},
    )
    token = login.json()["access_token"]

    logout = unauthenticated_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout.status_code == 204

    me = unauthenticated_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 401


async def test_login_bootstraps_initial_admin(unauthenticated_client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(settings, "initial_admin_email", "bootstrap@example.com")
    monkeypatch.setattr(settings, "initial_admin_password", "bootstrap-password")

    login = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "bootstrap@example.com", "password": "bootstrap-password"},
    )

    assert login.status_code == 200
    body = login.json()
    assert body["user"]["email"] == "bootstrap@example.com"
    assert body["user"]["role"] == "admin"


def test_protected_route_requires_auth(unauthenticated_client: TestClient) -> None:
    response = unauthenticated_client.get("/api/v1/sources")
    assert response.status_code == 401


def test_analyst_can_read_sources(analyst_client: TestClient) -> None:
    response = analyst_client.get("/api/v1/sources")
    assert response.status_code == 200


def test_analyst_cannot_create_source(analyst_client: TestClient) -> None:
    payload = {
        "name": "Blocked Source",
        "slug": "blocked-source",
        "category": "wire",
        "source_type": "rss",
    }
    response = analyst_client.post("/api/v1/sources", json=payload)
    assert response.status_code == 403


def test_operator_can_create_source(operator_client: TestClient) -> None:
    payload = {
        "name": "Operator Source",
        "slug": "operator-source",
        "category": "wire",
        "source_type": "rss",
    }
    response = operator_client.post("/api/v1/sources", json=payload)
    assert response.status_code == 201


def test_admin_can_create_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/users",
        json={
            "email": "new-analyst@example.com",
            "password": "secure-password",
            "role": "analyst",
        },
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new-analyst@example.com"
    assert response.json()["role"] == "analyst"


def test_operator_cannot_create_user(operator_client: TestClient) -> None:
    response = operator_client.post(
        "/api/v1/auth/users",
        json={
            "email": "blocked@example.com",
            "password": "secure-password",
            "role": "analyst",
        },
    )
    assert response.status_code == 403


async def test_inactive_user_cannot_login(unauthenticated_client: TestClient, db_session) -> None:
    db_session.add(
        User(
            email="inactive@example.com",
            password_hash=hash_password("correct-password"),
            role="analyst",
            is_active=False,
        )
    )
    await db_session.commit()

    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "correct-password"},
    )
    assert response.status_code == 401
