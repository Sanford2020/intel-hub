from fastapi import APIRouter

from app.api.v1.endpoints import agents, ai, health, stats
from app.modules.alerts.router import router as alerts_router
from app.modules.articles.router import router as articles_router
from app.modules.archives.router import router as archives_router
from app.modules.briefings.router import router as briefings_router
from app.modules.sources.router import router as sources_router

api_router = APIRouter()

api_router.include_router(health.router, prefix="/v1")
api_router.include_router(stats.router, prefix="/v1")
api_router.include_router(ai.router, prefix="/v1")
api_router.include_router(agents.router, prefix="/v1")
api_router.include_router(sources_router, prefix="/v1")
api_router.include_router(articles_router, prefix="/v1")
api_router.include_router(alerts_router, prefix="/v1")
api_router.include_router(briefings_router, prefix="/v1")
api_router.include_router(archives_router, prefix="/v1")
