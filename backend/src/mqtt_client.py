"""
MQTT client for Smart Home system.
Subscribes to device status updates and energy data from Raspberry Pi.
Publishes commands to devices.

Topic hierarchy:
  - device/{device_id}/status  (subscribe) - status updates from Raspberry Pi
  - device/{device_id}/energy  (subscribe) - energy readings from Raspberry Pi
    - home/{home_id}/face        (subscribe) - face images from Raspberry Pi
  - device/{device_id}/command (publish)   - commands to Raspberry Pi
  - smarthome/commands         (publish)   - legacy door/face commands
"""

import asyncio
import time
import json
import logging
import ssl
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.apis.face.service import enroll_face, upload_face_image, verify_face_image_for_home
from src.config.env import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_COMMAND_TOPIC,
    MQTT_USE_TLS,
)

_mqtt_client: mqtt.Client | None = None
_db_session_factory = None
_ws_manager = None
_event_loop: asyncio.AbstractEventLoop | None = None


def init_mqtt(session_factory, ws_manager):
    """Initialize MQTT with DB session factory and WS manager for callbacks."""
    global _db_session_factory, _ws_manager
    _db_session_factory = session_factory
    _ws_manager = ws_manager


def set_event_loop(loop: asyncio.AbstractEventLoop | None) -> None:
    global _event_loop
    _event_loop = loop


def _on_connect(client, userdata, flags, rc):
    logging.info(f"MQTT connected with result code {rc}")
    # Subscribe to all device status and energy topics
    client.subscribe("device/+/status")
    client.subscribe("device/+/energy")
    client.subscribe("home/+/face")
    logging.info("MQTT subscribed to device/+/status, device/+/energy and home/+/face")


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

    scope, scope_id, message_type = parts

    if message_type == 'status':
        _handle_device_status(scope_id, payload)
    elif message_type == 'energy':
        _handle_energy_data(scope_id, payload)
    elif message_type == 'face':
        _handle_face_image(scope_id, payload)


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
            payload_metadata = payload.get("metadata")
            if isinstance(payload_metadata, dict):
                for key, value in payload_metadata.items():
                    metadata[key] = value

            # Backward compatibility for older payloads (flat keys)
            legacy_keys = [
                "brightness",
                "temperature",
                "humidity",
                "targetTemp",
                "mode",
                "battery",
                "isLocked",
                "speed",
                "door",
                "buzzer",
                "distance_light",
                "distance_cm",
                "distance_alert",
                "gas_detected",
                "rain_detected",
                "state",
            ]
            for key in legacy_keys:
                if key in payload:
                    metadata[key] = payload[key]

            device.metadata_json = metadata

            db.commit()

            # Get home_id for WS broadcast
            room = db.query(Room).filter(Room.id == device.room_id).first()
            if room and _ws_manager:
                if _event_loop and _event_loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        _ws_manager.broadcast_device_update(
                            str(room.home_id),
                            device_id_str,
                            {"status": device.status, "online": device.online_status, "metadata": metadata},
                        ),
                        _event_loop,
                    )
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


def _handle_face_image(home_id: str, payload: dict):
    """Process face image payload from a device."""
    if not isinstance(payload, dict):
        logging.warning("MQTT face handler received non-object payload")
        return

    image_base64 = payload.get("image_base64")
    if not image_base64:
        logging.warning("MQTT face handler missing image_base64 for home %s", home_id)
        return

    action = str(payload.get("action", "verify")).strip().lower()
    door_device_id = str(payload.get("door_device_id") or "").strip()

    try:
        if action == "upload":
            saved, reason = upload_face_image(home_id, image_base64)
            logging.info(
                "MQTT face upload from %s saved=%s reason=%s",
                home_id,
                saved,
                reason,
            )
            return

        if action == "enroll":
            person_id = str(payload.get("person_id") or home_id)
            saved, image_path, reason = enroll_face(home_id, person_id, image_base64)
            logging.info(
                "MQTT face enroll from %s saved=%s image_path=%s reason=%s",
                home_id,
                saved,
                image_path,
                reason,
            )
            return

        verified, match_id, confidence, reason = verify_face_image_for_home(home_id, image_base64)
        logging.info(
            "MQTT face verify from %s verified=%s match_id=%s confidence=%s reason=%s",
            home_id,
            verified,
            match_id,
            confidence,
            reason,
        )
        if verified and door_device_id:
            publish_device_command(door_device_id, "open", None)
    except Exception as e:
        logging.error(f"MQTT face handler error: {e}")


def get_mqtt_client() -> mqtt.Client:
    global _mqtt_client
    if _mqtt_client is not None:
        return _mqtt_client

    client = mqtt.Client(client_id="backend-{}".format(int(time.time())))
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    if MQTT_USE_TLS or MQTT_BROKER_PORT == 8883:
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        logging.info(f"MQTT TLS enabled for {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")

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
