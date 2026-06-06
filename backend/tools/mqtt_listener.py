import json
import os
import ssl
import time

import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "0d847a93f8b9463487a312fdd241108a.s1.eu.hivemq.cloud")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "8883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "testuser")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "19122005Tri")
HOME_ID = os.getenv("HOME_ID") or os.getenv("DEFAULT_HOME_ID") or "home-001"
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "1").strip().lower() in {"1", "true", "yes", "on"}

LEGACY_STATUS_TOPIC = "smarthome/{}/status".format(HOME_ID)
LEGACY_SENSOR_TOPIC = "smarthome/{}/sensors".format(HOME_ID)


def _try_json(payload: bytes):
    try:
        return json.loads(payload.decode("utf-8"))
    except Exception:
        return None


def on_connect(client: mqtt.Client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[MQTT] Connected")
        client.subscribe("device/+/status", qos=1)
        client.subscribe("device/+/energy", qos=1)
        client.subscribe(LEGACY_STATUS_TOPIC, qos=1)
        client.subscribe(LEGACY_SENSOR_TOPIC, qos=1)
        print("[MQTT] Subscribed to device/+/status, device/+/energy, legacy status/sensors")
    else:
        print("[MQTT] Connect failed: {}".format(rc))


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    payload = _try_json(msg.payload)
    if payload is None:
        text = msg.payload.decode("utf-8", errors="replace")
        print("[MQTT] {} -> {}".format(msg.topic, text))
        return

    pretty = json.dumps(payload, ensure_ascii=False, indent=2)
    print("[MQTT] {} ->\n{}".format(msg.topic, pretty))


def build_client() -> mqtt.Client:
    client = mqtt.Client(client_id="listener-{}".format(int(time.time())))
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    if MQTT_USE_TLS or BROKER_PORT == 8883:
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

    client.on_connect = on_connect
    client.on_message = on_message
    return client


def main():
    print("[MQTT] host={} port={} tls={} username={}".format(
        BROKER_HOST,
        BROKER_PORT,
        MQTT_USE_TLS,
        MQTT_USERNAME or "",
    ))
    client = build_client()
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
