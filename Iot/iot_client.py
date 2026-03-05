import base64
import json
import os
import queue
import threading
import time
from typing import Optional, Tuple, Dict

import requests

try:
    import Adafruit_DHT
except ImportError:
    Adafruit_DHT = None

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
except ImportError:
    PiCamera = None
    PiRGBArray = None
    
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
        "door": state["door"],
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
DEVICE_LOOP_INTERVAL = float(os.getenv("DEVICE_LOOP_INTERVAL", "3"))

FACE_UPLOAD_URL = os.getenv("FACE_UPLOAD_URL", "http://192.168.1.201:8000/face/upload")
FACE_VERIFY_URL = os.getenv("FACE_VERIFY_URL", "http://192.168.1.201:8000/face/verify")
FACE_MODE = os.getenv("FACE_MODE", "verify").lower()
FACE_VERIFY_COOLDOWN = float(os.getenv("FACE_VERIFY_COOLDOWN", "5"))
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
CAPTURE_TIMEOUT_SECONDS = float(os.getenv("CAPTURE_TIMEOUT_SECONDS", "0.2"))
MIN_FACE_SIZE = int(os.getenv("MIN_FACE_SIZE", "80"))
DETECT_INTERVAL = float(os.getenv("DETECT_INTERVAL", "0.2"))
CAMERA_ISO = int(os.getenv("CAMERA_ISO", "800"))
CAMERA_SHUTTER_US = int(os.getenv("CAMERA_SHUTTER_US", "100000"))
CAMERA_EXPOSURE_MODE = os.getenv("CAMERA_EXPOSURE_MODE", "auto")
CAMERA_AWB_MODE = os.getenv("CAMERA_AWB_MODE", "auto")

state = {
    "light": "off",
    "fan": "off",
    "temperature_c": None,
    "humidity": None,
    "distance_cm": None,
    "distance_alert": None,
    "door": "closed",
}

stop_event = threading.Event()
face_queue = queue.Queue(maxsize=2)
last_verify_ts = 0.0


def log(message: str) -> None:
    print("[IOT] {}".format(message))


def init_gpio() -> None:
    if GPIO is None:
        log("RPi.GPIO not available; running in simulation mode.")
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
    log("publish_status")
    payload = {
        "device_id": DEVICE_ID,
        "light": state["light"],
        "fan": state["fan"],
        "temperature_c": state["temperature_c"],
        "humidity": state["humidity"],
        "door": state["door"],
        "timestamp": int(time.time()),
    }
    client.publish(STATUS_TOPIC, json.dumps(payload), qos=1, retain=False)


def publish_sensors(client: mqtt.Client) -> None:
    log("publish_sensors")
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
        log("read_dht: Adafruit_DHT not available")
        return

    sensor = get_dht_sensor()
    humidity, temperature = Adafruit_DHT.read_retry(sensor, DHT_PIN, retries=2, delay_seconds=1)
    if humidity is None or temperature is None:
        log("read_dht: failed to read (type={}, pin={})".format(DHT_TYPE, DHT_PIN))
        return

    state["temperature_c"] = round(float(temperature), 1)
    state["humidity"] = round(float(humidity), 1)
    log("read_dht: temp={}C humidity={}%%".format(state["temperature_c"], state["humidity"]))


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
    log("read_distance: {}cm alert={}".format(state["distance_cm"], state["distance_alert"]))


def apply_command(command: str) -> None:
    cmd = command.strip().lower()
    log("apply_command: {}".format(cmd))
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

    if cmd in {"door open", "door close"}:
        if cmd == "door open":
            _open_door_async()
        else:
            state["door"] = "closed"
            set_output(DOOR_PIN, False)
        return

    if cmd == "status":
        return


def _open_door_async() -> None:
    if GPIO is None:
        state["door"] = "open"
        return

    def _pulse() -> None:
        state["door"] = "open"
        log("door_open: pin {}".format(DOOR_PIN))
        set_output(DOOR_PIN, True)
        time.sleep(DOOR_OPEN_SECONDS)
        set_output(DOOR_PIN, False)
        state["door"] = "closed"

    threading.Thread(target=_pulse, daemon=True).start()


def on_connect(client: mqtt.Client, userdata, flags, rc, properties=None) -> None:
    if rc == 0:
        log("mqtt connected")
        client.subscribe(COMMAND_TOPIC, qos=1)
        publish_status(client)
    else:
        log("MQTT connect failed: {}".format(rc))


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    try:
        command = msg.payload.decode("utf-8")
    except UnicodeDecodeError:
        log("Invalid command payload")
        return

    apply_command(command)
    publish_status(client)
    log("Command '{}' applied. Light={}, Fan={}.".format(command, state["light"], state["fan"]))


def build_mqtt_client() -> Optional[mqtt.Client]:
    if mqtt is None:
        log("paho-mqtt not available; MQTT disabled.")
        return None

    client = mqtt.Client(client_id="device-{}".format(DEVICE_ID))
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
    return client


def capture_face_jpeg(
    camera_index: int = 0,
    timeout_seconds: float = 0.2,
    jpeg_quality: int = 85,
) -> Tuple[Optional[bytes], Optional[Tuple[int, int, int, int]]]:
    if cv2 is None:
        raise RuntimeError("OpenCV is not installed")

    if PiCamera is not None:
        log("capture: PiCamera")
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 24
        camera.exposure_mode = CAMERA_EXPOSURE_MODE
        camera.awb_mode = CAMERA_AWB_MODE
        camera.iso = CAMERA_ISO
        camera.shutter_speed = CAMERA_SHUTTER_US
        raw_capture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.5)

        try:
            deadline = time.monotonic() + timeout_seconds
            for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
                if time.monotonic() > deadline:
                    return None, None

                image = frame.array
                raw_capture.truncate(0)
                success, buffer = cv2.imencode(
                    ".jpg",
                    image,
                    [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
                )
                if success:
                    log("capture: PiCamera frame encoded")
                    return buffer.tobytes(), None

            return None, None
        finally:
            camera.close()

    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise RuntimeError("Unable to open camera index {}".format(camera_index))

    try:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            ok, frame = capture.read()
            if not ok:
                time.sleep(0.05)
                continue

            success, buffer = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
            )
            if success:
                log("capture: VideoCapture frame encoded")
                return buffer.tobytes(), None

        return None, None
    finally:
        capture.release()


def device_loop(client: Optional[mqtt.Client]) -> None:
    while not stop_event.is_set():
        log("device_loop tick")
        read_dht()
        read_distance()
        if client is not None:
            publish_status(client)
            publish_sensors(client)
        time.sleep(DEVICE_LOOP_INTERVAL)


def face_capture_loop() -> None:
    if cv2 is None:
        log("OpenCV not available; face upload disabled.")
        return

    while not stop_event.is_set():
        try:
            image_bytes, _ = capture_face_jpeg(
                camera_index=CAMERA_INDEX,
                timeout_seconds=CAPTURE_TIMEOUT_SECONDS,
            )
            if image_bytes:
                log("face_capture: got image")
                if face_queue.full():
                    try:
                        face_queue.get_nowait()
                    except queue.Empty:
                        pass
                face_queue.put(image_bytes)
        except Exception as exc:
            log("Face capture error: {}".format(exc))

        time.sleep(DETECT_INTERVAL)


def _post_face_image(url: str, image_bytes: bytes) -> Optional[dict]:
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    payload = {
        "device_id": DEVICE_ID,
        "image_base64": image_b64,
    }
    response = requests.post(url, json=payload, timeout=10.0)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return None


def face_send_loop() -> None:
    global last_verify_ts
    log("face_send_loop start mode={}".format(FACE_MODE))
    while not stop_event.is_set():
        try:
            image_bytes = face_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        try:
            if FACE_MODE == "verify":
                now = time.monotonic()
                if now - last_verify_ts < FACE_VERIFY_COOLDOWN:
                    log("face_verify: cooldown")
                    continue
                log("face_verify: sending to server")
                result = _post_face_image(FACE_VERIFY_URL, image_bytes)
                verified = bool(result.get("verified")) if isinstance(result, dict) else False
                log("face_verify: result={}".format(verified))
                if verified:
                    log("face_verify: match -> open door")
                    _open_door_async()
                    last_verify_ts = now
            else:
                log("face_upload: sending to server")
                _post_face_image(FACE_UPLOAD_URL, image_bytes)
        except Exception as exc:
            log("Face send error: {}".format(exc))


def main() -> None:
    log("iot_client starting")
    init_gpio()
    client = build_mqtt_client()

    threads = [
        threading.Thread(target=device_gpio_loop, args=(client,), daemon=True),
        threading.Thread(target=face_capture_loop, daemon=True),
        threading.Thread(target=face_send_loop, daemon=True),
    ]

    for thread in threads:
        thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        log("iot_client stopping")
        if client is not None:
            client.loop_stop()
        if GPIO is not None:
            GPIO.cleanup()


if __name__ == "__main__":
    main()
