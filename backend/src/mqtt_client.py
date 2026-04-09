import time
import json
import os
import ssl
import threading
from typing import Optional
import paho.mqtt.client as mqtt

from src.config.env import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_TOPIC_PREFIX,
    DEFAULT_HOME_ID,
    DEFAULT_DEVICE_ID,
)


_mqtt_client: Optional[mqtt.Client] = None
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "1").strip().lower() in {"1", "true", "yes", "on"}
_status_lock = threading.Lock()
_mqtt_connected = False
_last_message_topic = None
_last_message_ts = 0
_last_command = None
_last_command_ts = 0
_last_command_topic = None
# key "home_id/device_id" -> last merged status payload
_status_by_device: dict[str, dict] = {}


def _status_key(home_id: str, device_id: str) -> str:
    return "{}/{}".format(home_id, device_id)


def _topic_status_wildcard() -> str:
    return "{}/+/+/status".format(MQTT_TOPIC_PREFIX)


def _topic_sensor_wildcard() -> str:
    return "{}/+/+/sensors".format(MQTT_TOPIC_PREFIX)


def command_topic(home_id: str, device_id: str) -> str:
    return "{}/{}/{}/commands".format(MQTT_TOPIC_PREFIX, home_id, device_id)


def _parse_incoming_topic(topic: str) -> tuple[str, str, str] | None:
    parts = topic.split("/")
    if len(parts) != 4:
        return None
    if parts[0] != MQTT_TOPIC_PREFIX:
        return None
    channel = parts[3]
    if channel not in ("status", "sensors"):
        return None
    return parts[1], parts[2], channel


def _empty_status(home_id: str, device_id: str) -> dict:
    return {
        "home_id": home_id,
        "device_id": device_id,
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
        client.subscribe(sw, qos=1)
        client.subscribe(nw, qos=1)
        print("[backend-mqtt] connected; subscribed: {}, {}".format(sw, nw))
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

    key = _status_key(home_id, device_id)
    with _status_lock:
        if key not in _status_by_device:
            _status_by_device[key] = _empty_status(home_id, device_id)
        st = _status_by_device[key]
        if channel == "status":
            st.update(payload)
            st["home_id"] = home_id
            st["device_id"] = payload.get("device_id", device_id)
        elif channel == "sensors":
            st.update(
                {
                    "home_id": home_id,
                    "device_id": payload.get("device_id", device_id),
                    "distance_cm": payload.get("distance_cm"),
                    "distance_alert": payload.get("distance_alert"),
                    "distance_light": payload.get("distance_light", st.get("distance_light")),
                    "gas_detected": payload.get("gas_detected", st.get("gas_detected")),
                    "buzzer": payload.get("buzzer", st.get("buzzer")),
                    "rain_detected": payload.get("rain_detected", st.get("rain_detected")),
                    "timestamp": payload.get("timestamp", st.get("timestamp")),
                }
            )


def get_mqtt_client() -> mqtt.Client:
    global _mqtt_client
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


def publish_command(command: str, home_id: str, device_id: str) -> None:
    global _last_command, _last_command_ts, _last_command_topic
    topic = command_topic(home_id, device_id)
    client = get_mqtt_client()
    client.publish(topic, command, qos=1, retain=False)
    _last_command = command
    _last_command_ts = int(time.time())
    _last_command_topic = topic
    print("[backend-mqtt] publish command '{}' -> {}".format(command, topic))


def get_last_status(home_id: str, device_id: str) -> dict:
    get_mqtt_client()
    key = _status_key(home_id, device_id)
    with _status_lock:
        if key in _status_by_device:
            return dict(_status_by_device[key])
    return _empty_status(home_id, device_id)


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
            "default_home_id": DEFAULT_HOME_ID,
            "default_device_id": DEFAULT_DEVICE_ID,
            "known_devices": sorted(_status_by_device.keys()),
            "last_message_topic": _last_message_topic,
            "last_message_ts": _last_message_ts,
            "last_command": _last_command,
            "last_command_topic": _last_command_topic,
            "last_command_ts": _last_command_ts,
        }
