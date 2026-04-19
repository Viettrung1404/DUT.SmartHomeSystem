from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.apis.auth.controller import router as auth_router
from src.apis.homes.controller import router as homes_router
from src.apis.rooms.controller import router as rooms_router
from src.apis.devices.controller import router as devices_router
from src.apis.automations.controller import router as automations_router
from src.apis.energy.controller import router as energy_router
from src.apis.security.controller import router as security_router
from src.apis.face.controller import router as face_router
from src.apis.suggestions.controller import router as suggestions_router
from src.websocket import ws_manager

from src.apis.iot.controller import router as iot_router

def register_routes(app: FastAPI):
    # REST API routes
    app.include_router(auth_router)
    app.include_router(homes_router)
    app.include_router(rooms_router)
    app.include_router(devices_router)
    app.include_router(automations_router)
    app.include_router(energy_router)
    app.include_router(security_router)
    app.include_router(face_router)
    app.include_router(suggestions_router)

    # WebSocket endpoint
    @app.websocket("/ws/home/{home_id}")
    async def websocket_endpoint(websocket: WebSocket, home_id: str):
        await ws_manager.connect(websocket, home_id)
        try:
            while True:
                # Keep connection alive, handle incoming messages
                data = await websocket.receive_text()
                # Client can send ping or commands via WS
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket, home_id)

    app.include_router(iot_router)