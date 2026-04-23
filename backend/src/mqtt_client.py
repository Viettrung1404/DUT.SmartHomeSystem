"""
MQTT client for Smart Home system.
Subscribes to device status updates and energy data from Raspberry Pi.
Publishes commands to devices.

Topic hierarchy:
    - smarthome/{home_id}/status   (subscribe) - status updates from Raspberry Pi
    - smarthome/{home_id}/sensors  (subscribe) - sensors updates from Raspberry Pi
    - smarthome/{home_id}/commands (publish)   - commands to Raspberry Pi
  - smarthome/commands         (publish)   - legacy door/face commands
"""

import time
import json
import os
import ssl
import threading
import traceback
from typing import Optional
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from pathlib import Path
import errno
import urllib.request
import re

from src.config.env import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_TOPIC_PREFIX,
    DEFAULT_HOME_ID,
)
from src.database.core import SessionLocal
from src.entities.home import Home
from src.entities.device import Device
from src.entities.device_telemetry import DeviceTelemetry
from src.entities.device_identity_map import DeviceIdentityMap
from src.entities.user import User


_mqtt_client: Optional[mqtt.Client] = None
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "1").strip().lower() in {"1", "true", "yes", "on"}
_status_lock = threading.Lock()
_mqtt_connected = False
_last_message_topic = None
_last_message_ts = 0
_last_command = None
_last_command_ts = 0
_last_command_topic = None
# key "home_id" -> last merged status payload
_status_by_device: dict[str, dict] = {}


def _status_key(home_id: str) -> str:
    return home_id


def _topic_status_wildcard() -> str:
    return "{}/+/status".format(MQTT_TOPIC_PREFIX)


def _topic_sensor_wildcard() -> str:
    return "{}/+/sensors".format(MQTT_TOPIC_PREFIX)


def _legacy_topic_status_wildcard() -> str:
    return "{}/+/+/status".format(MQTT_TOPIC_PREFIX)


def _legacy_topic_sensor_wildcard() -> str:
    return "{}/+/+/sensors".format(MQTT_TOPIC_PREFIX)


def command_topic(home_id: str) -> str:
    return "{}/{}/commands".format(MQTT_TOPIC_PREFIX, home_id)


def _parse_incoming_topic(topic: str) -> tuple[str, str, str] | None:
    parts = topic.split("/")
    if len(parts) not in (3, 4):
        return None
    if parts[0] != MQTT_TOPIC_PREFIX:
        return None
    if len(parts) == 3:
        home_id = parts[1]
        channel = parts[2]
        device_key = ""
    else:
        home_id = parts[1]
        device_key = parts[2]
        channel = parts[3]
    if channel not in ("status", "sensors"):
        return None
    return home_id, device_key, channel


def _safe_uuid(value: str) -> UUID | None:
    try:
        return UUID(value)
    except Exception:
        return None


def _dbg_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # region agent log
    try:
        payload = {
            "sessionId": "6489de",
            "runId": os.getenv("DEBUG_RUN_ID", "pre-fix"),
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        line = json.dumps(payload, ensure_ascii=False) + "\n"

        # Preferred: send to debug ingest so logs always land in workspace debug-6489de.log
        try:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            ingest_urls = [
                # local (when running backend directly on host)
                "http://127.0.0.1:7337/ingest/21e0565d-4d78-4b91-89ce-e84b14b86e99",
                # docker on Windows/Mac: host network alias
                "http://host.docker.internal:7337/ingest/21e0565d-4d78-4b91-89ce-e84b14b86e99",
                # common linux bridge gateway (best-effort)
                "http://172.17.0.1:7337/ingest/21e0565d-4d78-4b91-89ce-e84b14b86e99",
            ]
            for url in ingest_urls:
                try:
                    req = urllib.request.Request(
                        url,
                        data=body,
                        headers={
                            "Content-Type": "application/json",
                            "X-Debug-Session-Id": "6489de",
                        },
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=0.35) as _:
                        return
                except Exception:
                    continue
        except Exception:
            pass

        # Fallback: print one-line NDJSON to stdout so docker logs contain it.
        try:
            print("[agentlog] " + json.dumps(payload, ensure_ascii=False))
        except Exception:
            pass

        # Candidate paths:
        # - workspace root when running locally
        # - /app/src when running in docker-compose (volume-mounted to ./backend/src)
        candidates: list[Path] = []
        candidates.append(Path.cwd() / "debug-6489de.log")
        fpath = Path(__file__).resolve()
        candidates.append(fpath.parent / "debug-6489de.log")
        # In case src is nested differently in runtime image
        candidates.append(fpath.parent.parent / "debug-6489de.log")
        candidates.append(fpath.parent.parent.parent / "debug-6489de.log")

        seen: set[str] = set()
        last_exc: Exception | None = None
        for p in candidates:
            key = str(p)
            if key in seen:
                continue
            seen.add(key)
            try:
                try:
                    p.parent.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    # If parent is not creatable, continue to next candidate
                    if e.errno not in (errno.EEXIST,):
                        raise
                with open(p, "a", encoding="utf-8") as f:
                    f.write(line)
                    try:
                        f.flush()
                        os.fsync(f.fileno())
                    except Exception:
                        pass
                return
            except Exception as exc:
                last_exc = exc
                continue

        if last_exc is not None:
            raise last_exc
    except Exception as exc:
        try:
            print(f"[backend-mqtt][debug] failed to write debug log: {exc}; tried={list(seen)}")
        except Exception:
            pass
    # endregion agent log


def _pick_owner_id_for_autoprovision(db: Session) -> UUID | None:
    admin = db.query(User.id).filter(User.is_admin.is_(True)).order_by(User.created_at.asc()).first()
    if admin:
        return admin[0]
    any_user = db.query(User.id).order_by(User.created_at.asc()).first()
    if any_user:
        return any_user[0]
    return None


def _key_variants(value: str) -> list[str]:
    """
    Generate common variants for external keys coming from MQTT topics,
    e.g. 'home-001' vs 'home 001' vs 'home001'. Keep it conservative.
    """
    raw = (value or "").strip()
    if not raw:
        return []
    lower = raw.lower()
    space = re.sub(r"[-_]+", " ", lower)
    space = re.sub(r"\s+", " ", space).strip()
    compact = re.sub(r"[^a-z0-9]+", "", lower)
    variants = {raw, lower, space, compact}
    return [v for v in variants if v]


def _ensure_identity_mapping(db: Session, home_key: str, device_key: str) -> tuple[UUID, UUID] | None:
    """
    Auto-provision Home + Device + DeviceIdentityMap for non-UUID mqtt keys.
    This is a pragmatic fallback to avoid dropping telemetry when provisioning wasn't done yet.
    """
    owner_id = _pick_owner_id_for_autoprovision(db)
    if owner_id is None:
        _dbg_log("H4", "mqtt_client.py:_ensure_identity_mapping", "autoprovision skipped: no users in DB", {"home_key": home_key, "device_key": device_key})
        return None

    home_variants = _key_variants(home_key)
    home = None
    if home_variants:
        home = db.query(Home).filter(Home.name.in_(home_variants)).first()
    if home is None:
        home = Home(id=uuid4(), owner_id=owner_id, name=home_key, address=None)
        db.add(home)
        db.flush()
        _dbg_log("H4", "mqtt_client.py:_ensure_identity_mapping", "autoprovision created home", {"home_id": str(home.id), "home_key": home_key, "owner_id": str(owner_id)})

    device = (
        db.query(Device)
        .filter(Device.home_id == home.id, Device.name.in_(_key_variants(device_key) or [device_key]))
        .first()
    )
    if device is None:
        device = Device(
            id=uuid4(),
            home_id=home.id,
            name=device_key,
            type="gateway",
            location=None,
            metadata_json={"mqtt_home_key": home_key, "mqtt_device_key": device_key},
            online_status=True,
            last_seen=datetime.now(timezone.utc),
        )
        db.add(device)
        db.flush()
        _dbg_log("H4", "mqtt_client.py:_ensure_identity_mapping", "autoprovision created device", {"device_id": str(device.id), "device_key": device_key, "home_id": str(home.id)})

    mapping = (
        db.query(DeviceIdentityMap)
        .filter(DeviceIdentityMap.home_key == home_key, DeviceIdentityMap.device_key == device_key)
        .first()
    )
    if mapping is None:
        mapping = DeviceIdentityMap(
            id=uuid4(),
            home_id=home.id,
            device_id=device.id,
            home_key=home_key,
            device_key=device_key,
        )
        db.add(mapping)
        db.flush()
        _dbg_log("H4", "mqtt_client.py:_ensure_identity_mapping", "autoprovision created identity map", {"mapping_id": str(mapping.id), "home_id": str(home.id), "device_id": str(device.id), "home_key": home_key, "device_key": device_key})
    else:
        if mapping.home_id != home.id or mapping.device_id != device.id:
            mapping.home_id = home.id
            mapping.device_id = device.id
            _dbg_log("H4", "mqtt_client.py:_ensure_identity_mapping", "autoprovision updated identity map", {"mapping_id": str(mapping.id), "home_id": str(home.id), "device_id": str(device.id), "home_key": home_key, "device_key": device_key})

    return home.id, device.id


def _resolve_home_and_source_device(db: Session, home_key: str, device_key: str) -> tuple[UUID, UUID] | None:
    _dbg_log("H1", "mqtt_client.py:_resolve_home_and_source_device", "resolve start", {"home_key": home_key, "device_key": device_key})
    mapping = (
        db.query(DeviceIdentityMap)
        .filter(DeviceIdentityMap.home_key == home_key, DeviceIdentityMap.device_key == device_key)
        .first()
    )
    if mapping:
        _dbg_log("H1", "mqtt_client.py:_resolve_home_and_source_device", "resolved via identity map", {"home_id": str(mapping.home_id), "device_id": str(mapping.device_id), "home_key": home_key, "device_key": device_key})
        return mapping.home_id, mapping.device_id

    home_uuid = _safe_uuid(home_key)
    device_uuid = _safe_uuid(device_key)
    _dbg_log("H2", "mqtt_client.py:_resolve_home_and_source_device", "uuid parse result", {"home_key": home_key, "device_key": device_key, "home_uuid": str(home_uuid) if home_uuid else None, "device_uuid": str(device_uuid) if device_uuid else None})
    if home_uuid and device_uuid:
        home_exists = db.query(Home.id).filter(Home.id == home_uuid).first() is not None
        device = db.query(Device).filter(Device.id == device_uuid, Device.home_id == home_uuid).first()
        if home_exists and device:
            db.add(
                DeviceIdentityMap(
                    id=uuid4(),
                    home_id=home_uuid,
                    device_id=device_uuid,
                    home_key=home_key,
                    device_key=device_key,
                )
            )
            return home_uuid, device_uuid

    if home_uuid and device_key == "home-default":
        fallback_device = (
            db.query(Device)
            .filter(Device.home_id == home_uuid)
            .order_by(Device.created_at.asc())
            .first()
        )
        if fallback_device is not None:
            db.add(
                DeviceIdentityMap(
                    id=uuid4(),
                    home_id=home_uuid,
                    device_id=fallback_device.id,
                    home_key=home_key,
                    device_key=device_key,
                )
            )
            print(
                "[backend-mqtt] fallback map created for home_key='{}' device_key='{}' -> device_id='{}'".format(
                    home_key, device_key, fallback_device.id
                )
            )
            return home_uuid, fallback_device.id

    # Non-UUID keys (e.g. home-001/raspi-01) need provisioning/mapping.
    if (home_uuid is None) or (device_uuid is None):
        ensured = _ensure_identity_mapping(db, home_key, device_key)
        if ensured is not None:
            _dbg_log("H4", "mqtt_client.py:_resolve_home_and_source_device", "resolved via autoprovision", {"home_id": str(ensured[0]), "device_id": str(ensured[1]), "home_key": home_key, "device_key": device_key})
            return ensured

    _dbg_log("H1", "mqtt_client.py:_resolve_home_and_source_device", "resolve failed", {"home_key": home_key, "device_key": device_key})
    return None


def _resolve_publish_home_key(db: Session, home_id: str, device_id: str | None = None) -> str:
    """
    Resolve MQTT home_key for command topic.
    Priority:
      1) mapping by device_id
      2) latest mapping by home_id
      3) fallback to provided home_id
    """
    device_uuid = _safe_uuid(device_id) if device_id else None
    if device_uuid is not None:
        mapping = db.query(DeviceIdentityMap).filter(DeviceIdentityMap.device_id == device_uuid).first()
        if mapping and mapping.home_key:
            _dbg_log(
                "IOT1",
                "mqtt_client.py:_resolve_publish_home_key",
                "resolved publish key by device",
                {
                    "home_id": home_id,
                    "device_id": device_id,
                    "home_key": mapping.home_key,
                },
            )
            return mapping.home_key

    home_uuid = _safe_uuid(home_id)
    if home_uuid is not None:
        mapping = (
            db.query(DeviceIdentityMap)
            .filter(DeviceIdentityMap.home_id == home_uuid)
            .order_by(DeviceIdentityMap.updated_at.desc())
            .first()
        )
        if mapping and mapping.home_key:
            _dbg_log(
                "IOT1",
                "mqtt_client.py:_resolve_publish_home_key",
                "resolved publish key by home",
                {
                    "home_id": home_id,
                    "device_id": device_id,
                    "home_key": mapping.home_key,
                },
            )
            return mapping.home_key

    _dbg_log(
        "IOT1",
        "mqtt_client.py:_resolve_publish_home_key",
        "fallback publish key to input home_id",
        {
            "home_id": home_id,
            "device_id": device_id,
        },
    )
    return home_id


def _to_onoff_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"on", "open", "true", "1", "strong", "weak", "detected", "wet"}


def _sync_home_devices_from_payload(db: Session, home_id: UUID, payload: dict, observed_at: datetime) -> None:
    devices = db.query(Device).filter(Device.home_id == home_id).all()
    for device in devices:
        metadata = device.metadata_json or {}
        iot_key = metadata.get("iot_key")

        if iot_key == "dht":
            temp = payload.get("temperature_c")
            hum = payload.get("humidity")
            if temp is None and hum is None:
                continue
            metadata["temperature_c"] = temp
            metadata["humidity"] = hum
            device.status = True
        else:
            if not iot_key or iot_key not in payload:
                continue
            value = payload.get(iot_key)
            metadata["last_value"] = value
            device.status = _to_onoff_bool(value)

        metadata["last_mqtt_timestamp"] = payload.get("timestamp")
        device.metadata_json = metadata
        device.online_status = True
        device.last_seen = observed_at


def _persist_payload(home_key: str, device_key: str, channel: str, payload: dict) -> None:
    if not isinstance(payload, dict):
        return

    observed_at = datetime.now(timezone.utc)
    with SessionLocal() as db:
        try:
            _dbg_log("H3", "mqtt_client.py:_persist_payload", "persist start", {"home_key": home_key, "device_key": device_key, "channel": channel, "payload_keys": sorted([str(k) for k in payload.keys()])[:50]})
            resolved = _resolve_home_and_source_device(db, home_key, device_key)
            if resolved is None:
                print(
                    "[backend-mqtt] unmapped topic key: home_key='{}' device_key='{}'; skipping DB persist".format(
                        home_key, device_key
                    )
                )
                _dbg_log("H1", "mqtt_client.py:_persist_payload", "persist skipped: unmapped", {"home_key": home_key, "device_key": device_key, "channel": channel})
                db.rollback()
                return

            home_id, source_device_id = resolved
            source_device = db.query(Device).filter(Device.id == source_device_id, Device.home_id == home_id).first()
            if source_device is None:
                _dbg_log("H3", "mqtt_client.py:_persist_payload", "persist skipped: resolved device missing", {"home_id": str(home_id), "device_id": str(source_device_id), "home_key": home_key, "device_key": device_key})
                db.rollback()
                return

            source_device.online_status = True
            source_device.last_seen = observed_at

            if channel == "status":
                _sync_home_devices_from_payload(db, home_id, payload, observed_at)

            for key, value in payload.items():
                if key in {"timestamp", "device_id"}:
                    continue
                db.add(
                    DeviceTelemetry(
                        id=uuid4(),
                        home_id=home_id,
                        source_device_id=source_device_id,
                        channel=channel,
                        metric_key=str(key),
                        metric_value=value,
                        recorded_at=observed_at,
                    )
                )

            db.commit()
            _dbg_log("H3", "mqtt_client.py:_persist_payload", "persist committed", {"home_id": str(home_id), "device_id": str(source_device_id), "channel": channel, "telemetry_count": max(0, len(payload) - (1 if "timestamp" in payload else 0) - (1 if "device_id" in payload else 0))})
        except Exception as exc:
            db.rollback()
            print("[backend-mqtt] persist failed: {}".format(exc))
            _dbg_log("H5", "mqtt_client.py:_persist_payload", "persist exception", {"home_key": home_key, "device_key": device_key, "channel": channel, "error": str(exc), "traceback": traceback.format_exc()[-2000:]})


def _empty_status(home_id: str) -> dict:
    return {
        "home_id": home_id,
        "den_khach": "unknown",
        "den_ngu": "unknown",
        "quat_khach": "unknown",
        "quat_ngu": "unknown",
        "light": "unknown",
        "fan": "unknown",
        "temperature_c": None,
        "humidity": None,
        "distance_cm": None,
        "distance_alert": None,
        "distance_light": "unknown",
        "gas_detected": None,
        "buzzer": "unknown",
        "rain_detected": None,
        "door": "unknown",
        "timestamp": 0,
    }


def _on_connect(client: mqtt.Client, userdata, flags, rc, properties=None) -> None:
    global _mqtt_connected
    if rc == 0:
        _mqtt_connected = True
        sw = _topic_status_wildcard()
        nw = _topic_sensor_wildcard()
        lsw = _legacy_topic_status_wildcard()
        lnw = _legacy_topic_sensor_wildcard()
        client.subscribe(sw, qos=1)
        client.subscribe(nw, qos=1)
        client.subscribe(lsw, qos=1)
        client.subscribe(lnw, qos=1)
        print("[backend-mqtt] connected; subscribed: {}, {}, {}, {}".format(sw, nw, lsw, lnw))
    else:
        _mqtt_connected = False
        print("[backend-mqtt] connect failed: {}".format(rc))


def _on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    global _last_message_topic, _last_message_ts
    parsed = _parse_incoming_topic(msg.topic)
    if not parsed:
        return

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception:
        return

    home_id, device_id, channel = parsed
    _last_message_topic = msg.topic
    _last_message_ts = int(time.time())

    key = _status_key(home_id)
    with _status_lock:
        if key not in _status_by_device:
            _status_by_device[key] = _empty_status(home_id)
        st = _status_by_device[key]
        if channel == "status":
            st.update(payload)
            st["home_id"] = home_id
        elif channel == "sensors":
            st.update(
                {
                    "home_id": home_id,
                    "distance_cm": payload.get("distance_cm"),
                    "distance_alert": payload.get("distance_alert"),
                    "distance_light": payload.get("distance_light", st.get("distance_light")),
                    "gas_detected": payload.get("gas_detected", st.get("gas_detected")),
                    "buzzer": payload.get("buzzer", st.get("buzzer")),
                    "rain_detected": payload.get("rain_detected", st.get("rain_detected")),
                    "timestamp": payload.get("timestamp", st.get("timestamp")),
                }
            )

    _persist_payload(home_id, device_id or "home-default", channel, payload)


def get_mqtt_client() -> mqtt.Client:
    global _mqtt_client
    _dbg_log("H0", "mqtt_client.py:get_mqtt_client", "get_mqtt_client called", {"cwd": str(Path.cwd()), "__file__": str(Path(__file__).resolve())})
    if _mqtt_client is not None:
        return _mqtt_client

    client = mqtt.Client(client_id="backend-{}".format(int(time.time())))
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    if MQTT_USE_TLS or MQTT_BROKER_PORT == 8883:
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        print("[backend-mqtt] tls enabled for {}:{}".format(MQTT_BROKER_HOST, MQTT_BROKER_PORT))

    client.on_connect = _on_connect
    client.on_message = _on_message
    print("[backend-mqtt] connecting -> {}:{} (prefix={}, status=*/*, sensors=*/*)".format(
        MQTT_BROKER_HOST,
        MQTT_BROKER_PORT,
        MQTT_TOPIC_PREFIX,
    ))
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
    client.loop_start()
    _mqtt_client = client
    return client


def publish_command(command: str, home_id: str, device_id: str | None = None) -> str:
    global _last_command, _last_command_ts, _last_command_topic
    with SessionLocal() as db:
        publish_home_key = _resolve_publish_home_key(db, home_id, device_id)
    topic = command_topic(publish_home_key)
    client = get_mqtt_client()
    client.publish(topic, command, qos=1, retain=False)
    _last_command = command
    _last_command_ts = int(time.time())
    _last_command_topic = topic
    print("[backend-mqtt] publish command '{}' -> {}".format(command, topic))
    return topic


def _latest_known_device_for_home(home_id: str) -> str | None:
    # Kept for compatibility with existing call sites.
    return None


def publish_command_home(command: str, home_id: str) -> str:
    _dbg_log(
        "IOT1",
        "mqtt_client.py:publish_command_home",
        "publish by home",
        {"home_id": home_id, "command": command},
    )
    return publish_command(command, home_id)


def get_last_status(home_id: str, device_id: str) -> dict:
    get_mqtt_client()
    key = _status_key(home_id)
    with _status_lock:
        if key in _status_by_device:
            return dict(_status_by_device[key])
    return _empty_status(home_id)


def get_last_status_by_home(home_id: str) -> dict:
    get_mqtt_client()

    # 1. đọc cache RAM trước (nhanh nhất)
    with _status_lock:
        candidates = [
            dict(payload)
            for payload in _status_by_device.values()
            if isinstance(payload, dict)
            and payload.get("home_id") == home_id
        ]

    if candidates:
        candidates.sort(key=lambda x: int(x.get("timestamp") or 0), reverse=True)
        latest = candidates[0]

        _dbg_log(
            "IOT2",
            "mqtt_client.py:get_last_status_by_home",
            "status from RAM",
            {
                "home_id": home_id,
                "timestamp": latest.get("timestamp"),
            },
        )
        return latest

    # 2. fallback DB (QUAN TRỌNG)
    _dbg_log(
        "IOT2",
        "mqtt_client.py:get_last_status_by_home",
        "fallback to DB",
        {"home_id": home_id},
    )

    db_status = _get_last_status_from_db(home_id)

    if db_status:
        _dbg_log(
            "IOT2",
            "mqtt_client.py:get_last_status_by_home",
            "status from DB",
            {
                "home_id": home_id,
                "timestamp": db_status.get("timestamp"),
            },
        )
        return db_status

    # 3. không có gì luôn
    return _empty_status(home_id)

def _get_last_status_from_db(home_id: str):
    try:
        from src.database.core import SessionLocal
        from src.entities.device_telemetry import DeviceTelemetry

        db = SessionLocal()

        records = (
            db.query(DeviceTelemetry)
            .filter(DeviceTelemetry.home_id == home_id)
            .order_by(DeviceTelemetry.recorded_at.desc())
            .limit(50)
            .all()
        )

        db.close()

        if not records:
            return None

        status = _empty_status(home_id)

        for r in records:
            status[r.metric_key] = r.metric_value
            status["timestamp"] = int(r.recorded_at.timestamp())

        return status

    except Exception as e:
        print("[DB ERROR]:", e)
        return None
    
def get_mqtt_debug() -> dict:
    get_mqtt_client()
    with _status_lock:
        return {
            "mqtt_connected": _mqtt_connected,
            "broker_host": MQTT_BROKER_HOST,
            "broker_port": MQTT_BROKER_PORT,
            "topic_prefix": MQTT_TOPIC_PREFIX,
            "status_subscription": _topic_status_wildcard(),
            "sensor_subscription": _topic_sensor_wildcard(),
            "legacy_status_subscription": _legacy_topic_status_wildcard(),
            "legacy_sensor_subscription": _legacy_topic_sensor_wildcard(),
            "default_home_id": DEFAULT_HOME_ID,
            "known_devices": sorted(_status_by_device.keys()),
            "last_message_topic": _last_message_topic,
            "last_message_ts": _last_message_ts,
            "last_command": _last_command,
            "last_command_topic": _last_command_topic,
            "last_command_ts": _last_command_ts,
        }
