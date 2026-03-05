import time
import paho.mqtt.client as mqtt

from src.config.env import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_COMMAND_TOPIC,
)


_mqtt_client: mqtt.Client | None = None


def get_mqtt_client() -> mqtt.Client:
    global _mqtt_client
    if _mqtt_client is not None:
        return _mqtt_client

    client = mqtt.Client(client_id="backend-{}".format(int(time.time())))
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
    client.loop_start()
    _mqtt_client = client
    return client


def publish_command(command: str) -> None:
    client = get_mqtt_client()
    client.publish(MQTT_COMMAND_TOPIC, command, qos=1, retain=False)
