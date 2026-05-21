"""Factor 1 & 4: Tools as structured outputs."""

from typing import Any, Callable, Awaitable

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Awaitable[Any]]] = {}
        self._definitions: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        handler: Callable[..., Awaitable[Any]],
        parameters: dict[str, Any] | None = None,
    ) -> None:
        self._tools[name] = handler
        self._definitions[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters or {"type": "object", "properties": {}},
        )

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._definitions.values())

    async def execute(self, tool: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        if tool not in self._tools:
            return {"success": False, "error": f"Unknown tool: {tool}"}
        try:
            result = await self._tools[tool](**(arguments or {}))
            return {"success": True, "result": result}
        except Exception as exc:
            return {"success": False, "error": str(exc)}


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    async def echo(message: str = "") -> str:
        return message

    async def human_approval(summary: str = "") -> dict[str, str]:
        """Factor 7: Contact humans — pauses run for approval."""
        return {"status": "pending_approval", "summary": summary}

    registry.register("echo", "Echo a message for testing", echo, {
        "type": "object",
        "properties": {"message": {"type": "string"}},
    })
    registry.register(
        "human_approval",
        "Request human approval before continuing",
        human_approval,
        {"type": "object", "properties": {"summary": {"type": "string"}}},
    )
    return registry
