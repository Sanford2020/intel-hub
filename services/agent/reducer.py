"""Factor 12: Stateless reducer — (state, event) → state."""

from services.agent.models import AgentRunState, ContextEvent, RunStatus


def reduce(state: AgentRunState, event: ContextEvent) -> AgentRunState:
    state.events.append(event)
    state.touch()
    return state


def mark_completed(state: AgentRunState, answer: str) -> AgentRunState:
    state.events.append(ContextEvent(role="assistant", content=answer))
    state.status = RunStatus.COMPLETED
    state.touch()
    return state


def mark_failed(state: AgentRunState, error: str) -> AgentRunState:
    state.events.append(ContextEvent(role="error", content=error))
    state.status = RunStatus.FAILED
    state.touch()
    return state
