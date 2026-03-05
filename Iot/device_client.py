import json
import os
import threading
import time
from typing import Dict

import paho.mqtt.client as mqtt

try:
    import Adafruit_DHT
except ImportError:
    Adafruit_DHT = None

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "test.mosquitto.org")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
COMMAND_TOPIC = os.getenv("MQTT_COMMAND_TOPIC", "smarthome/commands")
STATUS_TOPIC = os.getenv("MQTT_STATUS_TOPIC", "smarthome/status")
SENSOR_TOPIC = os.getenv("MQTT_SENSOR_TOPIC", "smarthome/sensors")
DEVICE_ID = os.getenv("DEVICE_ID", "raspi-01")

LIGHT_PIN = int(os.getenv("LIGHT_PIN", "17"))
LIGHT_PIN2 = int(os.getenv("LIGHT_PIN2", "22"))
FAN_PIN = int(os.getenv("FAN_PIN", "27"))
DOOR_PIN = int(os.getenv("DOOR_PIN", "5"))
DOOR_OPEN_SECONDS = float(os.getenv("DOOR_OPEN_SECONDS", "3"))
DHT_PIN = int(os.getenv("DHT_PIN", "4"))
DHT_TYPE = os.getenv("DHT_TYPE", "11")
TRIG_PIN = int(os.getenv("TRIG_PIN", "23"))
ECHO_PIN = int(os.getenv("ECHO_PIN", "24"))
DISTANCE_ALERT_CM = float(os.getenv("DISTANCE_ALERT_CM", "20"))

state = {
    "light": "off",
    "fan": "off",
    "temperature_c": None,
    "humidity": None,
    "distance_cm": None,
    "distance_alert": None,
    "door": "closed",
}


def init_gpio() -> None:
    if GPIO is None:
        print("RPi.GPIO not available; running in simulation mode.")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LIGHT_PIN, GPIO.OUT)
    GPIO.setup(LIGHT_PIN2, GPIO.OUT)
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.setup(DOOR_PIN, GPIO.OUT)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.output(LIGHT_PIN, GPIO.LOW)
    GPIO.output(LIGHT_PIN2, GPIO.LOW)
    GPIO.output(FAN_PIN, GPIO.LOW)
    GPIO.output(DOOR_PIN, GPIO.LOW)
    GPIO.output(TRIG_PIN, GPIO.LOW)


def set_output(pin: int, is_on: bool) -> None:
    if GPIO is None:
        return
    GPIO.output(pin, GPIO.HIGH if is_on else GPIO.LOW)


def publish_status(client: mqtt.Client) -> None:
    payload = {
        "device_id": DEVICE_ID,
        "light": state["light"],
        "fan": state["fan"],
        "temperature_c": state["temperature_c"],
        "humidity": state["humidity"],
        "timestamp": int(time.time()),
    }
    client.publish(STATUS_TOPIC, json.dumps(payload), qos=1, retain=False)


def publish_sensors(client: mqtt.Client) -> None:
    payload = {
        "device_id": DEVICE_ID,
        "distance_cm": state["distance_cm"],
        "distance_alert": state["distance_alert"],
        "timestamp": int(time.time()),
    }
    client.publish(SENSOR_TOPIC, json.dumps(payload), qos=1, retain=False)


def get_dht_sensor():
    if Adafruit_DHT is None:
        return None
    if DHT_TYPE == "22":
        return Adafruit_DHT.DHT22
    return Adafruit_DHT.DHT11


def read_dht() -> None:
    if Adafruit_DHT is None:
        return

    sensor = get_dht_sensor()
    humidity, temperature = Adafruit_DHT.read_retry(sensor, DHT_PIN, retries=2, delay_seconds=1)
    if humidity is None or temperature is None:
        return

    state["temperature_c"] = round(float(temperature), 1)
    state["humidity"] = round(float(humidity), 1)


def read_distance() -> None:
    if GPIO is None:
        return

    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(0.0002)
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    pulse_start = time.monotonic()
    timeout = pulse_start + 0.02
    while GPIO.input(ECHO_PIN) == 0:
        if time.monotonic() > timeout:
            return
        pulse_start = time.monotonic()

    pulse_end = time.monotonic()
    timeout = pulse_end + 0.02
    while GPIO.input(ECHO_PIN) == 1:
        if time.monotonic() > timeout:
            break
        pulse_end = time.monotonic()

    duration = pulse_end - pulse_start
    distance_cm = (duration * 34300.0) / 2.0
    state["distance_cm"] = round(float(distance_cm), 1)
    state["distance_alert"] = distance_cm <= DISTANCE_ALERT_CM
    if state["distance_alert"]:
        GPIO.output(LIGHT_PIN2, GPIO.HIGH)
    else:
        GPIO.output(LIGHT_PIN2, GPIO.LOW)


def apply_command(command: str) -> None:
    cmd = command.strip().lower()
    if cmd in {"on", "off", "toggle"}:
        cmd = "light {}".format(cmd)
    if cmd in {"light on", "light off", "light toggle"}:
        if cmd == "light on":
            state["light"] = "on"
        elif cmd == "light off":
            state["light"] = "off"
        else:
            state["light"] = "off" if state["light"] == "on" else "on"
        set_output(LIGHT_PIN, state["light"] == "on")
        return

    if cmd in {"fan on", "fan off", "fan toggle"}:
        if cmd == "fan on":
            state["fan"] = "on"
        elif cmd == "fan off":
            state["fan"] = "off"
        else:
            state["fan"] = "off" if state["fan"] == "on" else "on"
        set_output(FAN_PIN, state["fan"] == "on")
        return

    if cmd == "all on":
        state["light"] = "on"
        state["fan"] = "on"
        set_output(LIGHT_PIN, True)
        set_output(FAN_PIN, True)
        return

    if cmd == "all off":
        state["light"] = "off"
        state["fan"] = "off"
        set_output(LIGHT_PIN, False)
        set_output(FAN_PIN, False)
        return

    if cmd == "status":
        return

    if cmd in {"door open", "door close"}:
        if cmd == "door open":
            _open_door_async()
        else:
            state["door"] = "closed"
            set_output(DOOR_PIN, False)
        return


def _open_door_async() -> None:
    if GPIO is None:
        state["door"] = "open"
        return

    def _pulse() -> None:
        state["door"] = "open"
        set_output(DOOR_PIN, True)
        time.sleep(DOOR_OPEN_SECONDS)
        set_output(DOOR_PIN, False)
        state["door"] = "closed"

    threading.Thread(target=_pulse, daemon=True).start()


def on_connect(client: mqtt.Client, userdata, flags, rc, properties=None) -> None:
    if rc == 0:
        client.subscribe(COMMAND_TOPIC, qos=1)
        publish_status(client)
    else:
        print("MQTT connect failed: {}".format(rc))


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    try:
        command = msg.payload.decode("utf-8")
    except UnicodeDecodeError:
        print("Invalid command payload")
        return

    apply_command(command)
    publish_status(client)
    print("Command '{}' applied. Light={}, Fan={}.".format(command, state["light"], state["fan"]))


def main() -> None:
    init_gpio()
    client = mqtt.Client(client_id="device-{}".format(DEVICE_ID))
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
    try:
        while True:
            print("Reading DHT sensor...")
            read_dht()
            print("Reading distance sensor...")
            read_distance()
            print("Publishing status...")
            publish_status(client)
            print("Publishing sensors...")
            publish_sensors(client)
            time.sleep(3)
    finally:
        client.loop_stop()
        if GPIO is not None:
            GPIO.cleanup()


if __name__ == "__main__":
    main()
