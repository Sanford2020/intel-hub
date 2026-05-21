from typing import Any

from openai import AsyncOpenAI

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.openai_api_key
        self.base_url = base_url or settings.openai_base_url
        self.model = model or settings.openai_model
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def _has_real_api_key(self) -> bool:
        key = (self.api_key or "").strip()
        if not key:
            return False
        placeholders = {"your-api-key-here", "changeme", "sk-xxx", "x"}
        return key.lower() not in placeholders and not key.startswith("your-")

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if not self._has_real_api_key():
            user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            logger.warning("ai_api_key_missing", model=self.model)
            mock_intel = (
                '{"summary":"Mock intelligence analysis of the article.",'
                '"tags":["mock","intel"],"entities":[{"name":"Example Org","type":"org"}],'
                '"relevance_score":7.5,"language":"en"}'
            )
            return {
                "content": mock_intel if response_format else f"[Mock AI] Received: {user_msg[:200]}",
                "model": "mock",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            }

        try:
            kwargs: dict[str, Any] = {
                "model": model or self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = await self.client.chat.completions.create(**kwargs)

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            }
        except Exception as e:
            logger.error("AI chat error", error=str(e))
            raise

    async def structured_output(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        return await self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )


ai_client = AIClient()
