from fastapi import APIRouter

from app.schemas.base import APIResponse
from app.services.ai_service import ChatRequest, ChatResponseData, run_chat

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=APIResponse[ChatResponseData])
async def chat(body: ChatRequest) -> APIResponse[ChatResponseData]:
    data = await run_chat(body)
    return APIResponse(success=True, data=data)


@router.get("/prompts")
async def list_prompts() -> APIResponse[list[str]]:
    from services.ai.prompts.base import prompt_manager

    return APIResponse(success=True, data=prompt_manager.list_prompts())
