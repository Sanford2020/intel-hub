"""Factor 5 & 6: Unified state with pause/resume."""

from services.agent.models import AgentRunState, RunStatus

_store: dict[str, AgentRunState] = {}


class StateStore:
    def create(self, state: AgentRunState) -> AgentRunState:
        _store[state.id] = state
        return state

    def get(self, run_id: str) -> AgentRunState | None:
        return _store.get(run_id)

    def save(self, state: AgentRunState) -> AgentRunState:
        _store[state.id] = state
        return state

    def pause(self, run_id: str) -> AgentRunState | None:
        state = _store.get(run_id)
        if state:
            state.status = RunStatus.PAUSED
            state.touch()
        return state

    def resume(self, run_id: str) -> AgentRunState | None:
        state = _store.get(run_id)
        if state and state.status == RunStatus.PAUSED:
            state.status = RunStatus.RUNNING
            state.touch()
        return state

    def list_runs(self) -> list[AgentRunState]:
        return list(_store.values())


state_store = StateStore()
