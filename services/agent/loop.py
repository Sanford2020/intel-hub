"""Factor 8: Own your control flow — explicit agent loop."""

import json

from services.agent.context import ContextWindow
from services.agent.models import AgentRunState, AgentStep, RunStatus
from services.agent.reducer import mark_completed, mark_failed
from services.agent.state import state_store
from services.agent.tools import ToolRegistry, build_default_registry
from services.ai.client import ai_client


class AgentLoop:
    def __init__(self, tools: ToolRegistry | None = None, max_steps: int = 10) -> None:
        self.tools = tools or build_default_registry()
        self.context = ContextWindow()
        self.max_steps = max_steps

    async def run(self, state: AgentRunState) -> AgentRunState:
        state.status = RunStatus.RUNNING
        state_store.save(state)

        for _ in range(self.max_steps):
            if state.status == RunStatus.PAUSED:
                break

            step = await self._determine_next_step(state)
            if step.intent == "done":
                mark_completed(state, step.final_answer or "Done")
                break

            if step.intent == "human_approval" or step.tool == "human_approval":
                await self.tools.execute("human_approval", step.arguments)
                state.status = RunStatus.PAUSED
                state.touch()
                break

            if step.tool:
                self.context.append(state, "assistant", json.dumps(step.model_dump()))
                result = await self.tools.execute(step.tool, step.arguments)
                self.context.append(state, "tool", json.dumps(result))
                if not result.get("success"):
                    self.context.append_error(state, result.get("error", "tool failed"))
            else:
                self.context.append(state, "assistant", step.reasoning or step.intent)
        else:
            mark_failed(state, "Max steps exceeded")

        return state_store.save(state)

    async def _determine_next_step(self, state: AgentRunState) -> AgentStep:
        if not ai_client._has_real_api_key():
            return self._mock_step(state)

        system = (
            "You are a focused agent. Respond with JSON only: "
            '{"intent":"tool_call|done|human_approval","tool":"name|null",'
            '"arguments":{},"final_answer":"string|null","reasoning":"string"}'
        )
        messages = [{"role": "system", "content": system}, *self.context.build_messages(state)]
        result = await ai_client.structured_output(messages=messages, temperature=0.2)
        try:
            return AgentStep.model_validate_json(result["content"] or "{}")
        except Exception:
            return AgentStep(intent="done", final_answer=result.get("content", "Completed"))

    def _mock_step(self, state: AgentRunState) -> AgentStep:
        tool_events = [e for e in state.events if e.role == "tool"]
        if not tool_events:
            return AgentStep(intent="tool_call", tool="echo", arguments={"message": state.goal})
        return AgentStep(intent="done", final_answer=f"Mock completed: {state.goal}")
