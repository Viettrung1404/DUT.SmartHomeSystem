# -*- coding: utf-8 -*-
import argparse
import json
import os
import threading
import ssl

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


def parse_value(text):
    if text is None:
        return None
    lowered = text.strip().lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def main():
    parser = argparse.ArgumentParser(description="Send MQTT command to IoT device")
    parser.add_argument("device_id", help="Target device UUID")
    parser.add_argument("command", help="Command name")
    parser.add_argument("--value", help="Optional command value")
    parser.add_argument("--raw", action="store_true", help="Send raw payload without JSON wrapper")
    args = parser.parse_args()

    if mqtt is None:
        raise SystemExit("paho-mqtt is not installed")

    if load_dotenv is not None:
        load_dotenv()

    broker_host = os.getenv(
        "MQTT_BROKER_HOST",
        "0d847a93f8b9463487a312fdd241108a.s1.eu.hivemq.cloud",
    )
    broker_port = int(os.getenv("MQTT_BROKER_PORT", "8883"))
    username = os.getenv("MQTT_USERNAME", "testuser")
    password = os.getenv("MQTT_PASSWORD", "19122005Tri")
    use_tls = os.getenv("MQTT_USE_TLS", "1").strip().lower() in {"1", "true", "yes", "on"}

    masked_password = "***" if password else ""
    print(
        "mqtt config host={} port={} tls={} username={} password={}".format(
            broker_host,
            broker_port,
            use_tls,
            username or "",
            masked_password,
        )
    )

    published_event = threading.Event()

    def on_publish(client, userdata, mid):
        published_event.set()

    client = mqtt.Client(client_id="mqtt-test")
    client.on_publish = on_publish
    if username:
        client.username_pw_set(username, password or None)
    if use_tls or broker_port == 8883:
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

    client.connect(broker_host, broker_port, keepalive=30)
    client.loop_start()

    if args.raw:
        payload = args.command if args.value is None else "{} {}".format(args.command, args.value)
    else:
        payload = {"command": args.command}
        value = parse_value(args.value)
        if value is not None:
            payload["value"] = value
        payload = json.dumps(payload)

    topic = "device/{}/command".format(args.device_id)
    client.publish(topic, payload, qos=1, retain=False)
    published_event.wait(timeout=3.0)
    client.loop_stop()
    client.disconnect()
    print("Published to {}: {}".format(topic, payload))


if __name__ == "__main__":
    main()
