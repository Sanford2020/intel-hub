"""Factor 3: Own your context window."""

from services.agent.models import AgentRunState, ContextEvent


class ContextWindow:
    def __init__(self, max_events: int = 50) -> None:
        self.max_events = max_events

    def build_messages(self, state: AgentRunState) -> list[dict[str, str]]:
        events = state.events[-self.max_events :]
        return [{"role": e.role, "content": e.content} for e in events if e.role != "error"]

    def append(self, state: AgentRunState, role: str, content: str, **metadata: object) -> None:
        state.events.append(
            ContextEvent(role=role, content=content, metadata=dict(metadata))
        )
        state.touch()

    def append_error(self, state: AgentRunState, error: str) -> None:
        """Factor 9: Compact errors into context."""
        compact = error[:500]
        state.events.append(ContextEvent(role="error", content=compact))
        state.touch()
