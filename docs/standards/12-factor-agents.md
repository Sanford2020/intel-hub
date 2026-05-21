# 12-Factor Agents (Engineering Layer)

Source: [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents) (Apache-2.0)

Production principles for LLM-powered software. Implemented in this scaffold as `services/agent/`.

| # | Factor | Scaffold implementation |
|---|--------|-------------------------|
| 1 | Natural language → tool calls | `services/agent/tools.py` — ToolRegistry |
| 2 | Own your prompts | `/prompts/*.yaml`, `/prompts/agents/` |
| 3 | Own your context window | `services/agent/context.py` — ContextWindow |
| 4 | Tools are structured outputs | Pydantic tool schemas in `tools.py` |
| 5 | Unify execution + business state | `services/agent/state.py` — AgentRunState |
| 6 | Launch / Pause / Resume | `POST /api/v1/agents/runs/{id}/pause|resume` |
| 7 | Contact humans with tool calls | `human_approval` tool stub |
| 8 | Own your control flow | `services/agent/loop.py` — explicit loop, no black-box framework |
| 9 | Compact errors into context | `context.append_error()` |
| 10 | Small, focused agents | One role per agent in `agents/registry.yaml` |
| 11 | Trigger from anywhere | API, Celery worker, cron-ready |
| 12 | Stateless reducer | `services/agent/reducer.py` — `(state, event) → state` |

## Agent loop (canonical)

```python
context = ContextWindow.from_event(initial_event)
while True:
    step = await llm.next_step(context)  # structured JSON
    context.append(step)
    if step.intent == "done":
        break
    if step.intent == "human_approval":
        await state.pause(run_id)
        break
    result = await tools.execute(step)
    context.append(result)
state.save(context)
```

## API

- `POST /api/v1/agents/runs` — start run
- `GET /api/v1/agents/runs/{id}` — get state
- `POST /api/v1/agents/runs/{id}/resume` — resume after pause
