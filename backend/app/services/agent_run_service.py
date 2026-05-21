"""Agent run service — wraps 12-factor runtime."""

from pydantic import BaseModel, Field

from services.agent import AgentLoop, AgentRunState, RunStatus, state_store
from services.agent.context import ContextWindow
from services.agent.models import ContextEvent


class CreateRunRequest(BaseModel):
    goal: str = Field(..., min_length=1, max_length=10000)
    agent_role: str = Field(default="default")
    initial_context: str | None = None


class RunSummary(BaseModel):
    id: str
    status: RunStatus
    goal: str
    agent_role: str
    event_count: int
    created_at: str
    updated_at: str


def _to_summary(state: AgentRunState) -> RunSummary:
    return RunSummary(
        id=state.id,
        status=state.status,
        goal=state.goal,
        agent_role=state.agent_role,
        event_count=len(state.events),
        created_at=state.created_at,
        updated_at=state.updated_at,
    )


async def create_run(body: CreateRunRequest) -> AgentRunState:
    state = AgentRunState(goal=body.goal, agent_role=body.agent_role)
    ctx = ContextWindow()
    ctx.append(state, "system", f"Agent role: {body.agent_role}")
    ctx.append(state, "user", body.initial_context or body.goal)
    state_store.create(state)
    loop = AgentLoop()
    return await loop.run(state)


def get_run(run_id: str) -> AgentRunState | None:
    return state_store.get(run_id)


async def resume_run(run_id: str) -> AgentRunState | None:
    state = state_store.resume(run_id)
    if not state:
        return None
    loop = AgentLoop()
    return await loop.run(state)


def list_runs() -> list[RunSummary]:
    return [_to_summary(s) for s in state_store.list_runs()]
