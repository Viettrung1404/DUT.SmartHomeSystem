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
    MQTT_COMMAND_TOPIC,
    MQTT_STATUS_TOPIC,
    MQTT_SENSOR_TOPIC,
)


_mqtt_client: Optional[mqtt.Client] = None
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "1").strip().lower() in {"1", "true", "yes", "on"}
_status_lock = threading.Lock()
_mqtt_connected = False
_last_message_topic = None
_last_message_ts = 0
_last_command = None
_last_command_ts = 0
_last_status = {
    "device_id": "unknown",
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
        client.subscribe(MQTT_STATUS_TOPIC, qos=1)
        client.subscribe(MQTT_SENSOR_TOPIC, qos=1)
        print("[backend-mqtt] connected; subscribed: {}, {}".format(MQTT_STATUS_TOPIC, MQTT_SENSOR_TOPIC))
    else:
        _mqtt_connected = False
        print("[backend-mqtt] connect failed: {}".format(rc))


def _on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    global _last_message_topic, _last_message_ts
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception:
        return

    _last_message_topic = msg.topic
    _last_message_ts = int(time.time())

    with _status_lock:
        if msg.topic == MQTT_STATUS_TOPIC:
            _last_status.update(payload)
        elif msg.topic == MQTT_SENSOR_TOPIC:
            _last_status.update(
                {
                    "device_id": payload.get("device_id", _last_status.get("device_id")),
                    "distance_cm": payload.get("distance_cm"),
                    "distance_alert": payload.get("distance_alert"),
                    "distance_light": payload.get("distance_light", _last_status.get("distance_light")),
                    "gas_detected": payload.get("gas_detected", _last_status.get("gas_detected")),
                    "buzzer": payload.get("buzzer", _last_status.get("buzzer")),
                    "rain_detected": payload.get("rain_detected", _last_status.get("rain_detected")),
                    "timestamp": payload.get("timestamp", _last_status.get("timestamp")),
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
    print("[backend-mqtt] connecting -> {}:{} (cmd={}, status={}, sensor={})".format(
        MQTT_BROKER_HOST,
        MQTT_BROKER_PORT,
        MQTT_COMMAND_TOPIC,
        MQTT_STATUS_TOPIC,
        MQTT_SENSOR_TOPIC,
    ))
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
    client.loop_start()
    _mqtt_client = client
    return client


def publish_command(command: str) -> None:
    global _last_command, _last_command_ts
    client = get_mqtt_client()
    client.publish(MQTT_COMMAND_TOPIC, command, qos=1, retain=False)
    _last_command = command
    _last_command_ts = int(time.time())
    print("[backend-mqtt] publish command '{}' -> {}".format(command, MQTT_COMMAND_TOPIC))


def get_last_status() -> dict:
    get_mqtt_client()
    with _status_lock:
        return dict(_last_status)


def get_mqtt_debug() -> dict:
    get_mqtt_client()
    with _status_lock:
        return {
            "mqtt_connected": _mqtt_connected,
            "broker_host": MQTT_BROKER_HOST,
            "broker_port": MQTT_BROKER_PORT,
            "command_topic": MQTT_COMMAND_TOPIC,
            "status_topic": MQTT_STATUS_TOPIC,
            "sensor_topic": MQTT_SENSOR_TOPIC,
            "last_message_topic": _last_message_topic,
            "last_message_ts": _last_message_ts,
            "last_command": _last_command,
            "last_command_ts": _last_command_ts,
            "last_status": dict(_last_status),
        }
