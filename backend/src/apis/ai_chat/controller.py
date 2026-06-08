from fastapi import APIRouter
from uuid import UUID

from src.apis.ai_chat import models, service
from src.apis.auth.service import CurrentUser
from src.apis.devices import models as device_models
from src.apis.devices import service as device_service
from src.database.core import DbSession

router = APIRouter(prefix="/chat", tags=["ai-chat"])


@router.post("/smart-home", response_model=models.SmartHomeChatResponse)
async def smart_home_chat(
    body: models.SmartHomeChatRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    user_id = current_user.get_uuid()
    service.ensure_home_member(db, body.home_id, user_id)
    session_id = body.session_id or current_user.session_id or f"{user_id}:{body.home_id}"
    ai_response = await service.forward_chat({
        "session_id": str(session_id),
        "user_id": str(user_id),
        "home_id": str(body.home_id),
        "message": body.message,
        "timezone": body.timezone,
    })

    commands = ai_response.get("device_commands") or []
    if not commands and ai_response.get("device_command"):
        commands = [ai_response["device_command"]]
    if not commands:
        return ai_response

    command_results = []
    for command in commands:
        executed_device = device_service.send_command(
            db,
            UUID(command["device_id"]),
            user_id,
            device_models.DeviceCommandRequest(
                command=command["command"],
                value=command.get("value"),
            ),
        )
        command_results.append(device_service.to_response(executed_device).model_dump(mode="json"))

    ai_response["command_executed"] = True
    ai_response["command_result"] = command_results[0] if len(command_results) == 1 else None
    ai_response["command_results"] = command_results
    if len(commands) == 1:
        command = commands[0]
        ai_response["answer"] = (
            f"Đã thực hiện lệnh {command['command']} cho "
            f"{command.get('device_name') or command.get('device_slug') or 'thiết bị'}."
        )
    else:
        command_names = ", ".join(
            f"{command.get('device_name') or command.get('device_slug') or 'thiết bị'} ({command['command']})"
            for command in commands
        )
        ai_response["answer"] = f"Đã thực hiện {len(commands)} lệnh: {command_names}."
    return ai_response


@router.post("/smart-home/reset")
async def reset_smart_home_chat(
    body: models.ResetSmartHomeChatRequest,
    current_user: CurrentUser,
):
    return await service.reset_memory({
        "session_id": body.session_id,
        "user_id": str(current_user.get_uuid()),
    })
