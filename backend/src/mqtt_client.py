"""
MQTT client for Smart Home system.
Subscribes to device status updates and energy data from Raspberry Pi.
Publishes commands to devices.

Topic hierarchy:
  - device/{device_id}/status  (subscribe) - status updates from Raspberry Pi
  - device/{device_id}/energy  (subscribe) - energy readings from Raspberry Pi
  - device/{device_id}/command (publish)   - commands to Raspberry Pi
  - smarthome/commands         (publish)   - legacy door/face commands
"""

import time
import json
import logging
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.config.env import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_COMMAND_TOPIC,
)

_mqtt_client: mqtt.Client | None = None
_db_session_factory = None
_ws_manager = None


def init_mqtt(session_factory, ws_manager):
    """Initialize MQTT with DB session factory and WS manager for callbacks."""
    global _db_session_factory, _ws_manager
    _db_session_factory = session_factory
    _ws_manager = ws_manager


def _on_connect(client, userdata, flags, rc):
    logging.info(f"MQTT connected with result code {rc}")
    # Subscribe to all device status and energy topics
    client.subscribe("device/+/status")
    client.subscribe("device/+/energy")
    logging.info("MQTT subscribed to device/+/status and device/+/energy")


def _on_message(client, userdata, msg):
    """Handle incoming MQTT messages from Raspberry Pi."""
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        logging.warning(f"Invalid MQTT payload on {topic}: {msg.payload}")
        return

    parts = topic.split('/')
    if len(parts) != 3:
        return

    _, device_id_str, message_type = parts

    if message_type == 'status':
        _handle_device_status(device_id_str, payload)
    elif message_type == 'energy':
        _handle_energy_data(device_id_str, payload)


def _handle_device_status(device_id_str: str, payload: dict):
    """Update device status in DB and broadcast via WebSocket."""
    if not _db_session_factory:
        return
    try:
        from src.entities.device import Device
        from src.entities.room import Room

        db = _db_session_factory()
        try:
            device_id = UUID(device_id_str)
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                logging.warning(f"MQTT: unknown device {device_id_str}")
                return

            # Update device fields
            if 'status' in payload:
                device.status = payload['status']
            if 'online' in payload:
                device.online_status = payload['online']
            device.last_seen = datetime.now(timezone.utc)

            # Update metadata
            metadata = device.metadata_json or {}
            for key in ['brightness', 'temperature', 'humidity', 'targetTemp', 'mode', 'battery', 'isLocked']:
                if key in payload:
                    metadata[key] = payload[key]
            device.metadata_json = metadata

            db.commit()

            # Get home_id for WS broadcast
            room = db.query(Room).filter(Room.id == device.room_id).first()
            if room and _ws_manager:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(
                            _ws_manager.broadcast_device_update(
                                str(room.home_id), device_id_str,
                                {"status": device.status, "online": device.online_status, "metadata": metadata}
                            )
                        )
                except RuntimeError:
                    pass
        finally:
            db.close()
    except Exception as e:
        logging.error(f"MQTT status handler error: {e}")


def _handle_energy_data(device_id_str: str, payload: dict):
    """Store energy reading from device."""
    if not _db_session_factory:
        return
    try:
        from src.entities.energy_log import EnergyLog

        db = _db_session_factory()
        try:
            device_id = UUID(device_id_str)
            power_usage = payload.get('power_usage', payload.get('value', 0))
            log = EnergyLog(id=uuid4(), device_id=device_id, power_usage=float(power_usage))
            db.add(log)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logging.error(f"MQTT energy handler error: {e}")


def get_mqtt_client() -> mqtt.Client:
    global _mqtt_client
    if _mqtt_client is not None:
        return _mqtt_client

    client = mqtt.Client(client_id="backend-{}".format(int(time.time())))
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    client.on_connect = _on_connect
    client.on_message = _on_message

    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
        client.loop_start()
        _mqtt_client = client
        logging.info(f"MQTT client connected to {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    except Exception as e:
        logging.warning(f"MQTT connection failed: {e}. Running without MQTT.")
        _mqtt_client = client  # Store even on failure to avoid retry spam

    return client


def publish_command(command: str) -> None:
    """Publish a command. Can be JSON string or simple string."""
    client = get_mqtt_client()
    client.publish(MQTT_COMMAND_TOPIC, command, qos=1, retain=False)


def publish_device_command(device_id: str, command: str, value=None) -> None:
    """Publish a structured command to a specific device."""
    client = get_mqtt_client()
    topic = f"device/{device_id}/command"
    payload = json.dumps({"command": command, "value": value})
    client.publish(topic, payload, qos=1, retain=False)
    logging.info(f"MQTT published to {topic}: {payload}")
