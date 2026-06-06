from src.entities.models import HomeUser

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.apis.auth.controller import router as auth_router
from src.apis.auth import service as auth_service
from src.apis.users.controller import admin_router as admin_users_router
from src.apis.users.controller import router as users_router
from src.apis.homes.controller import router as homes_router
from src.apis.rooms.controller import router as rooms_router
from src.apis.devices.controller import router as devices_router
from src.apis.automations.controller import router as automations_router
from src.apis.energy.controller import router as energy_router
from src.apis.security.controller import router as security_router
from src.apis.suggestions.controller import router as suggestions_router
from src.apis.face.controller import router as face_router
from src.apis.assistant.controller import router as assistant_router
from src.websocket import ws_manager
from src.database.core import SessionLocal

from uuid import UUID

def register_routes(app: FastAPI):
    # REST API routes
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(admin_users_router)
    app.include_router(homes_router)
    app.include_router(rooms_router)
    app.include_router(devices_router)
    app.include_router(automations_router)
    app.include_router(energy_router)
    app.include_router(security_router)
    app.include_router(suggestions_router)
    app.include_router(face_router)
    app.include_router(assistant_router)

    # WebSocket endpoint
    @app.websocket("/ws/home/{home_id}")
    async def websocket_endpoint(websocket: WebSocket, home_id: str):
        # Phase A: minimal WS auth via access token + home membership check.
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008)
            return

        try:
            token_data = auth_service.verify_token(token, expected_type="access")
            user_id = token_data.get_uuid()
            if not user_id:
                await websocket.close(code=1008)
                return
        except Exception:
            await websocket.close(code=1008)
            return

        try:
            home_uuid = UUID(home_id)
        except Exception:
            await websocket.close(code=1008)
            return

        db = SessionLocal()
        try:
            member = (
                db.query(HomeUser)
                .filter(HomeUser.home_id == home_uuid, HomeUser.user_id == user_id)
                .first()
            )
            if not member:
                await websocket.close(code=1008)
                return
        finally:
            db.close()

        await ws_manager.connect(websocket, home_id)
        try:
            while True:
                # Keep connection alive, handle incoming messages
                data = await websocket.receive_text()
                # Client can send ping or commands via WS
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket, home_id)
