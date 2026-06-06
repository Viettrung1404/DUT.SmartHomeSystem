from fastapi import APIRouter, Depends

from app.agent.agent import SmartHomeAgent
from app.api.dependencies import require_api_key
from app.memory.memory_store import memory_store
from app.schemas.chat_schema import ChatRequest, ChatResponse, ResetMemoryRequest

router = APIRouter(prefix="/v1/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, dependencies=[Depends(require_api_key)])
def chat(request: ChatRequest):
    return SmartHomeAgent().handle(request)


@router.post("/reset", dependencies=[Depends(require_api_key)])
def reset_memory(request: ResetMemoryRequest):
    memory_store.reset(request.session_id, request.user_id)
    return {"success": True}

