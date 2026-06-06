from fastapi import APIRouter, HTTPException, status

from src.apis.assistant import models, service
from src.apis.auth.service import CurrentUser
from src.database.core import DbSession
from src.exceptions import ForbiddenError


router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=models.AssistantChatResponse)
async def assistant_chat(
    body: models.AssistantChatRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    try:
        home = service.resolve_home_for_user(db, current_user.get_uuid(), body.home_id)
        home_context = service.build_home_context(db, home, current_user.get_uuid())
    except ForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    try:
        ai_payload = await service.call_ai_assistant(body.message, home_context)
    except service.AssistantProxyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    should_execute, skip_reason = service.should_autorun(ai_payload, body.execute_if_confident)
    if should_execute:
        execution_payload = service.execute_action_draft(db, current_user.get_uuid(), ai_payload)
    else:
        execution_payload = {
            "status": "skipped",
            "reason": skip_reason or "Lenh chua nam trong tap auto-run",
        }

    return models.AssistantChatResponse(
        reply_text=ai_payload.get("reply_text") or "",
        nlu=ai_payload.get("nlu") or {},
        grounding=ai_payload.get("grounding") or {},
        action_draft=ai_payload.get("action_draft"),
        follow_up_question=ai_payload.get("follow_up_question"),
        safety_flags=ai_payload.get("safety_flags") or [],
        execution=models.AssistantExecutionResult(**execution_payload),
        home_id=str(home.id),
    )
