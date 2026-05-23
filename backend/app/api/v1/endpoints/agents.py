from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User
from app.modules.auth.dependencies import require_operator_write
from app.schemas.base import APIResponse
from app.services.agent_run_service import (
    CreateRunRequest,
    RunSummary,
    create_run,
    get_run,
    list_runs,
    resume_run,
)
from services.agent.models import AgentRunState

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/runs", response_model=APIResponse[RunSummary])
async def start_run(
    body: CreateRunRequest,
    _user: User = Depends(require_operator_write),
) -> APIResponse[RunSummary]:
    state = await create_run(body)
    from app.services.agent_run_service import _to_summary

    return APIResponse(success=True, data=_to_summary(state))


@router.get("/runs", response_model=APIResponse[list[RunSummary]])
async def get_runs() -> APIResponse[list[RunSummary]]:
    return APIResponse(success=True, data=list_runs())


@router.get("/runs/{run_id}", response_model=APIResponse[AgentRunState])
async def get_run_by_id(run_id: str) -> APIResponse[AgentRunState]:
    state = get_run(run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found")
    return APIResponse(success=True, data=state)


@router.post("/runs/{run_id}/resume", response_model=APIResponse[RunSummary])
async def resume_run_by_id(
    run_id: str,
    _user: User = Depends(require_operator_write),
) -> APIResponse[RunSummary]:
    state = await resume_run(run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found or not paused")
    from app.services.agent_run_service import _to_summary

    return APIResponse(success=True, data=_to_summary(state))


@router.get("/tools")
async def list_agent_tools() -> APIResponse[list[dict]]:
    from services.agent.tools import build_default_registry

    tools = build_default_registry().list_tools()
    return APIResponse(success=True, data=[t.model_dump() for t in tools])
