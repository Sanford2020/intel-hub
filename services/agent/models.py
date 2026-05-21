"""12-Factor Agent runtime models."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStep(BaseModel):
    intent: str
    tool: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    final_answer: str | None = None
    reasoning: str | None = None


class ContextEvent(BaseModel):
    role: str  # user | assistant | tool | system | error
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class AgentRunState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    status: RunStatus = RunStatus.PENDING
    goal: str = ""
    agent_role: str = "default"
    events: list[ContextEvent] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC).isoformat()
