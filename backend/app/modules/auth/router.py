from typing import Any

from fastapi import APIRouter, Depends, Response, status

from app.models.user import User
from app.modules.auth.dependencies import (
    get_auth_service,
    get_current_token_payload,
    get_current_user,
    require_admin,
)
from app.modules.auth.schemas import LoginRequest, LoginResponse, UserCreate, UserRead
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    user, token, expires_at = await service.authenticate(
        payload.email,
        payload.password,
    )
    return LoginResponse(
        access_token=token,
        expires_at=expires_at,
        user=UserRead.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    payload: dict[str, Any] = Depends(get_current_token_payload),
    service: AuthService = Depends(get_auth_service),
) -> None:
    jti = payload.get("jti")
    if isinstance(jti, str):
        await service.revoke_session(jti)
    response.status_code = status.HTTP_204_NO_CONTENT


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    _admin: User = Depends(require_admin),
    service: AuthService = Depends(get_auth_service),
) -> UserRead:
    user = await service.create_user(payload.email, payload.password, payload.role)
    return UserRead.model_validate(user)
