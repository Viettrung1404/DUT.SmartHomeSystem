"""
MQTT client for Smart Home system.
Subscribes to device status updates and energy data from Raspberry Pi.
Publishes commands to devices.

Topic hierarchy:
  - device/{device_id}/status  (subscribe) - status updates from Raspberry Pi
  - device/{device_id}/energy  (subscribe) - energy readings from Raspberry Pi
  - home/{home_id}/face        (subscribe) - face images from Raspberry Pi
  - smarthome/{home_id}/status (subscribe) - legacy gateway status
  - smarthome/{home_id}/sensors (subscribe) - legacy gateway sensors
  - device/{device_id}/command (publish)   - commands to Raspberry Pi
  - smarthome/{home_id}/commands (publish) - legacy Raspberry Pi commands
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

_LEGACY_METADATA_KEYS = [
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
    "den_khach",
    "den_ngu",
    "quat_khach",
    "quat_ngu",
]


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
    client.subscribe("smarthome/+/status")
    client.subscribe("smarthome/+/sensors")
    logging.info(
        "MQTT subscribed to device/+/status, device/+/energy, home/+/face, "
        "smarthome/+/status and smarthome/+/sensors"
    )


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

    if scope == "device" and message_type == 'status':
        _handle_device_status(scope_id, payload)
    elif scope == "device" and message_type == 'energy':
        _handle_energy_data(scope_id, payload)
    elif scope == "home" and message_type == 'face':
        _handle_face_image(scope_id, payload)
    elif scope == "smarthome" and message_type in {"status", "sensors"}:
        _handle_legacy_home_status(scope_id, payload)


def _enum_value(value) -> str:
    return str(getattr(value, "value", value) or "").strip().lower()


def _room_alias(room) -> str:
    text = " ".join(
        str(part or "").lower()
        for part in (getattr(room, "name", ""), getattr(room, "icon", ""))
    )
    if any(token in text for token in ("khach", "khách", "living", "sofa")):
        return "khach"
    if any(token in text for token in ("ngu", "ngủ", "bed", "master")):
        return "ngu"
    return ""


def _device_text(device) -> str:
    return " ".join(
        str(part or "").lower()
        for part in (
            getattr(device, "name", ""),
            getattr(device, "slug", ""),
            _enum_value(getattr(device, "type", "")),
        )
    )


def _merge_status_payload(existing_state: dict | None, payload: dict) -> dict:
    state = dict(existing_state or {})
    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
        state.update(metadata)

    for key in _LEGACY_METADATA_KEYS:
        if key in payload:
            state[key] = payload[key]

    if "status" in payload and isinstance(payload["status"], bool):
        state["power"] = "ON" if payload["status"] else "OFF"

    return state


def _set_device_state(db, device, payload: dict, online: bool | None = None) -> tuple[bool, dict]:
    from sqlalchemy.orm.attributes import flag_modified
    from src.entities.models import DeviceState

    if device.state is None:
        device.state = DeviceState(device_id=device.id, is_online=False, state={})
        db.add(device.state)

    if online is None:
        online = bool(payload.get("online", True))
    device.state.is_online = online
    device.state.last_updated = datetime.now(timezone.utc)
    device.state.state = _merge_status_payload(device.state.state, payload)
    flag_modified(device.state, "state")
    return online, device.state.state


def _broadcast_device_state(home_id: str, device_id: str, online: bool, metadata: dict) -> None:
    if not _ws_manager:
        return
    if _event_loop and _event_loop.is_running():
        asyncio.run_coroutine_threadsafe(
            _ws_manager.broadcast_device_update(
                home_id,
                device_id,
                {
                    "status": metadata.get("power") == "ON",
                    "online": online,
                    "metadata": metadata,
                },
            ),
            _event_loop,
        )


def _handle_device_status(device_id_str: str, payload: dict):
    """Update device status in DB and broadcast via WebSocket."""
    if not _db_session_factory:
        return
    try:
        from src.entities.models import Device, Room

        db = _db_session_factory()
        try:
            device_id = UUID(device_id_str)
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                logging.warning(f"MQTT: unknown device {device_id_str}")
                return

            online, metadata = _set_device_state(db, device, payload)
            db.commit()

            # Get home_id for WS broadcast
            room = db.query(Room).filter(Room.id == device.room_id).first()
            if room:
                _broadcast_device_state(str(room.home_id), device_id_str, online, metadata)
        finally:
            db.close()
    except Exception as e:
        logging.error(f"MQTT status handler error: {e}")


def _legacy_payload_for_device(device, room, payload: dict) -> dict:
    device_type = _enum_value(device.type)
    room_key = _room_alias(room)
    text = _device_text(device)
    device_payload = {"online": True}

    if device_type == "light" and room_key:
        value = payload.get(f"den_{room_key}")
        if value is not None:
            is_on = str(value).strip().lower() == "on"
            device_payload["status"] = is_on
            device_payload["metadata"] = {"state": "on" if is_on else "off"}
    elif device_type == "fan" and room_key:
        value = payload.get(f"quat_{room_key}")
        if value is not None:
            speed = str(value).strip().lower()
            device_payload["status"] = speed != "off"
            device_payload["metadata"] = {"speed": speed}
    elif device_type in {"lock", "door", "curtain"} or "door" in text or "cua" in text or "cửa" in text:
        value = payload.get("door")
        if value is not None:
            door = str(value).strip().lower()
            device_payload["status"] = door == "open"
            device_payload["metadata"] = {"door": door, "isLocked": door != "open"}
    elif "gas" in text or "khi" in text or "khí" in text:
        if "gas_detected" in payload:
            device_payload["status"] = bool(payload["gas_detected"])
            device_payload["metadata"] = {"gas_detected": bool(payload["gas_detected"])}
    elif "rain" in text or "mua" in text or "mưa" in text:
        if "rain_detected" in payload:
            device_payload["status"] = bool(payload["rain_detected"])
            device_payload["metadata"] = {"rain_detected": bool(payload["rain_detected"])}
    elif "distance" in text or "khoang" in text or "khoảng" in text or "pir" in text:
        metadata = {}
        for key in ("distance_cm", "distance_alert", "distance_light"):
            if key in payload:
                metadata[key] = payload[key]
        if metadata:
            device_payload["status"] = bool(payload.get("distance_alert", False))
            device_payload["metadata"] = metadata
    elif any(token in text for token in ("temp", "humid", "nhiet", "nhiệt", "am", "ẩm")):
        metadata = {}
        for key in ("temperature", "humidity"):
            if key in payload:
                metadata[key] = payload[key]
        if metadata:
            device_payload["status"] = True
            device_payload["metadata"] = metadata

    if "metadata" not in device_payload:
        device_payload["metadata"] = {}
    return device_payload


def _handle_legacy_home_status(home_id_str: str, payload: dict):
    """Update current DB state from the old Raspberry Pi gateway topics."""
    if not _db_session_factory:
        return
    try:
        from src.entities.models import Device, Room

        db = _db_session_factory()
        try:
            home_id = UUID(home_id_str)
            devices = (
                db.query(Device, Room)
                .join(Room, Device.room_id == Room.id)
                .filter(Room.home_id == home_id)
                .all()
            )
            for device, room in devices:
                device_payload = _legacy_payload_for_device(device, room, payload)
                online, metadata = _set_device_state(db, device, device_payload, online=True)
                _broadcast_device_state(home_id_str, str(device.id), online, metadata)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logging.error(f"MQTT legacy status handler error: {e}")


def _handle_energy_data(device_id_str: str, payload: dict):
    """Store energy reading from device."""
    if not _db_session_factory:
        return
    try:
        from src.entities.models import EnergyLog

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
        elif verified:
            _publish_legacy_home_command(get_mqtt_client(), home_id, "door open")
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


def _legacy_command_for_device(device, room, command: str, value=None) -> tuple[str | None, str | None]:
    device_type = _enum_value(device.type)
    room_key = _room_alias(room)
    cmd = str(command or "").strip().lower()
    text = _device_text(device)
    home_id = str(room.home_id) if room else None

    if cmd == "toggle" and isinstance(value, bool):
        cmd = "turn_on" if value else "turn_off"

    if device_type == "light" and room_key:
        if cmd in {"turn_on", "on"}:
            return f"den {room_key} on", home_id
        if cmd in {"turn_off", "off"}:
            return f"den {room_key} off", home_id
        if cmd == "toggle":
            return f"den {room_key} toggle", home_id

    if device_type == "fan" and room_key:
        if cmd in {"turn_on", "on"}:
            return f"quat {room_key} on", home_id
        if cmd in {"turn_off", "off"}:
            return f"quat {room_key} off", home_id
        if cmd == "toggle":
            return f"quat {room_key} toggle", home_id
        if cmd in {"set_speed", "set_fan_speed"} and value is not None:
            speed = str(value).strip().lower()
            if speed in {"weak", "low", "yeu"}:
                return f"quat {room_key} weak", home_id
            if speed in {"strong", "high", "manh", "max"}:
                return f"quat {room_key} strong", home_id
            if speed == "off":
                return f"quat {room_key} off", home_id
        if cmd in {"weak", "strong"}:
            return f"quat {room_key} {cmd}", home_id

    if device_type in {"lock", "door", "curtain"} or "door" in text or "cua" in text or "cửa" in text:
        if cmd in {"open", "door_open", "unlock", "turn_on", "on"}:
            return "door open", home_id
        if cmd in {"close", "door_close", "lock", "turn_off", "off"}:
            return "door close", home_id

    if "buzzer" in text:
        if cmd in {"turn_on", "on"}:
            return "buzzer on", home_id
        if cmd in {"turn_off", "off"}:
            return "buzzer off", home_id
        if cmd == "toggle":
            return "buzzer toggle", home_id

    return None, home_id


def _resolve_legacy_command(device_id: str, command: str, value=None) -> tuple[str | None, str | None]:
    if not _db_session_factory:
        return None, None
    try:
        from src.entities.models import Device, Room

        db = _db_session_factory()
        try:
            device_uuid = UUID(str(device_id))
            row = (
                db.query(Device, Room)
                .join(Room, Device.room_id == Room.id)
                .filter(Device.id == device_uuid)
                .first()
            )
            if not row:
                return None, None
            device, room = row
            return _legacy_command_for_device(device, room, command, value)
        finally:
            db.close()
    except Exception as e:
        logging.warning(f"Legacy MQTT command resolve failed: {e}")
        return None, None


def _publish_legacy_home_command(client: mqtt.Client, home_id: str, command: str) -> None:
    topic = f"smarthome/{home_id}/commands"
    client.publish(topic, command, qos=1, retain=False)
    logging.info("MQTT legacy command published to %s: %s", topic, command)


def publish_device_command(device_id: str, command: str, value=None) -> None:
    """Publish a structured command and a legacy command for old Raspberry Pi clients."""
    client = get_mqtt_client()
    topic = f"device/{device_id}/command"
    payload = json.dumps({"command": command, "value": value})
    client.publish(topic, payload, qos=1, retain=False)

    legacy_command, home_id = _resolve_legacy_command(device_id, command, value)
    if legacy_command and home_id:
        _publish_legacy_home_command(client, home_id, legacy_command)
        return

    # Old face payloads can send HOME_ID as door_device_id when no device map exists.
    if str(command).strip().lower() in {"open", "door_open"}:
        try:
            UUID(str(device_id))
            _publish_legacy_home_command(client, str(device_id), "door open")
        except Exception:
            pass
