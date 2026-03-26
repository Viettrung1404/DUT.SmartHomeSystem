"""
WebSocket connection manager for real-time device status updates.
Supports per-home rooms so broadcasts target only relevant users.
"""

import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Manages WebSocket connections grouped by home_id."""

    def __init__(self):
        # home_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, home_id: str):
        await websocket.accept()
        if home_id not in self.active_connections:
            self.active_connections[home_id] = set()
        self.active_connections[home_id].add(websocket)
        logging.info(f"WS connected: home={home_id}, total={len(self.active_connections[home_id])}")

    def disconnect(self, websocket: WebSocket, home_id: str):
        if home_id in self.active_connections:
            self.active_connections[home_id].discard(websocket)
            if not self.active_connections[home_id]:
                del self.active_connections[home_id]
        logging.info(f"WS disconnected: home={home_id}")

    async def broadcast_to_home(self, home_id: str, message: dict):
        """Send a message to all connections for a specific home."""
        if home_id not in self.active_connections:
            return
        disconnected = set()
        data = json.dumps(message)
        for connection in self.active_connections[home_id]:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.add(connection)
        for conn in disconnected:
            self.active_connections[home_id].discard(conn)

    async def broadcast_device_update(self, home_id: str, device_id: str, status: dict):
        """Broadcast a device status change to all home members."""
        await self.broadcast_to_home(home_id, {
            "type": "device_update",
            "device_id": device_id,
            "data": status,
        })

    async def broadcast_security_alert(self, home_id: str, event: dict):
        """Broadcast a security alert to all home members."""
        await self.broadcast_to_home(home_id, {
            "type": "security_alert",
            "data": event,
        })

    async def broadcast_automation_trigger(self, home_id: str, automation: dict):
        """Broadcast when an automation is triggered."""
        await self.broadcast_to_home(home_id, {
            "type": "automation_triggered",
            "data": automation,
        })


# Global singleton
ws_manager = ConnectionManager()
