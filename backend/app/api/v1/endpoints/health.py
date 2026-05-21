from datetime import UTC, datetime

from fastapi import APIRouter

from app.config import settings
from app.schemas.base import APIResponse

router = APIRouter(tags=["health"])


class HealthData(APIResponse[dict[str, str]]):
    pass


@router.get("/health")
async def health_check() -> dict[str, object]:
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    }


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"message": "pong"}
