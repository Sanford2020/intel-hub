from pydantic import BaseModel, Field

from services.ai.client import ai_client
from services.ai.prompts.base import prompt_manager


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=32000)
    system_prompt: str | None = None
    prompt_template: str | None = Field(
        default=None,
        description="Load system prompt from /prompts/{name}.yaml or .txt",
    )


class ChatResponseData(BaseModel):
    content: str
    model: str
    usage: dict[str, int] | None = None


async def run_chat(body: ChatRequest) -> ChatResponseData:
    messages: list[dict[str, str]] = []

    if body.prompt_template:
        system = prompt_manager.get_system_prompt(body.prompt_template)
        messages.append({"role": "system", "content": system})
    elif body.system_prompt:
        messages.append({"role": "system", "content": body.system_prompt})

    messages.append({"role": "user", "content": body.prompt})

    response_format = None
    if body.prompt_template:
        try:
            definition = prompt_manager.load_yaml(body.prompt_template)
            if definition.output_format and definition.output_format.get("type") == "json_schema":
                response_format = {"type": "json_object"}
        except FileNotFoundError:
            pass

    if response_format:
        result = await ai_client.structured_output(messages=messages)
    else:
        result = await ai_client.chat(messages=messages)

    return ChatResponseData(
        content=result["content"] or "",
        model=result["model"],
        usage=result.get("usage"),
    )
