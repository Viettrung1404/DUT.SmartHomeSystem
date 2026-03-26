import json
import os
import threading
import time
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request
import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "test.mosquitto.org")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
COMMAND_TOPIC = os.getenv("MQTT_COMMAND_TOPIC", "smarthome/commands")
STATUS_TOPIC = os.getenv("MQTT_STATUS_TOPIC", "smarthome/status")
SENSOR_TOPIC = os.getenv("MQTT_SENSOR_TOPIC", "smarthome/sensors")
WEB_PORT = int(os.getenv("WEB_PORT", "8001"))
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")

app = Flask(__name__)

status_lock = threading.Lock()
last_status: Dict[str, Any] = {
    "device_id": "unknown",
    "light": "unknown",
    "fan": "unknown",
    "temperature_c": None,
    "humidity": None,
    "distance_cm": None,
    "distance_alert": None,
    "timestamp": 0,
}


def on_connect(client: mqtt.Client, userdata, flags, rc, properties=None) -> None:
    if rc == 0:
        client.subscribe(STATUS_TOPIC, qos=1)
        client.subscribe(SENSOR_TOPIC, qos=1)
    else:
        print("MQTT connect failed: {}".format(rc))


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return

    with status_lock:
        if msg.topic == STATUS_TOPIC:
            last_status.update(payload)
        elif msg.topic == SENSOR_TOPIC:
            last_status.update(
                {
                    "device_id": payload.get("device_id", last_status.get("device_id")),
                    "distance_cm": payload.get("distance_cm"),
                    "distance_alert": payload.get("distance_alert"),
                }
            )


def build_mqtt_client() -> mqtt.Client:
    client = mqtt.Client(client_id="web-{}".format(int(time.time())))
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
    return client


mqtt_client = build_mqtt_client()


@app.route("/")
def index():
    return render_template("index.html", backend_base_url=BACKEND_BASE_URL)


@app.route("/api/command", methods=["POST"])
def api_command():
    data = request.get_json(silent=True) or {}
    command = str(data.get("command", "")).strip().lower()
    if command in {"on", "off", "toggle"}:
        command = "light {}".format(command)

    if command not in {
        "light on",
        "light off",
        "light toggle",
        "fan on",
        "fan off",
        "fan toggle",
        "all on",
        "all off",
        "status",
    }:
        return jsonify({"error": "Invalid command"}), 400

    mqtt_client.publish(COMMAND_TOPIC, command, qos=1, retain=False)
    return jsonify({"ok": True, "command": command})


@app.route("/api/status")
def api_status():
    with status_lock:
        return jsonify(last_status)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, use_reloader=False)
