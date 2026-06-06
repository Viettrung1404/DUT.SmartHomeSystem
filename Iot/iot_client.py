# -*- coding: utf-8 -*-
import base64
import json
import os
import queue
import ssl
import threading
import time


def _load_env_file(path):
    if not path or not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except Exception:
        return

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key:
            os.environ.setdefault(key, value)


_load_env_file(os.path.join(os.path.dirname(__file__), ".env"))

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

try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None

DEVICE_MAP_PATH = os.getenv("DEVICE_MAP_PATH", "device_map.json")
DOOR_DEVICE_ID = os.getenv("DOOR_DEVICE_ID", "")
DEVICE_REGISTRY = None

BROKER_HOST = os.getenv(
    "MQTT_BROKER_HOST",
    "0d847a93f8b9463487a312fdd241108a.s1.eu.hivemq.cloud"
)

BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "8883"))

MQTT_USERNAME = os.getenv("MQTT_USERNAME", "testuser")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "19122005Tri")

HOME_ID = os.getenv("HOME_ID") or os.getenv("DEFAULT_HOME_ID") or "home-001"

# Each Raspberry Pi (or controller) should be registered as a backend Device.
# Phase A uses a single DEVICE_ID to publish status and receive commands.
DEVICE_ID = os.getenv("DEVICE_ID") or os.getenv("IOT_DEVICE_ID") or ""


# Legacy home-scoped topics (kept for backward compatibility)
LEGACY_COMMAND_TOPIC = "smarthome/{}/commands".format(HOME_ID)
LEGACY_STATUS_TOPIC = "smarthome/{}/status".format(HOME_ID)
LEGACY_SENSOR_TOPIC = "smarthome/{}/sensors".format(HOME_ID)

# New per-device contract (preferred)
DEVICE_COMMAND_TOPIC = "device/{}/command".format(DEVICE_ID) if DEVICE_ID else None
DEVICE_STATUS_TOPIC = "device/{}/status".format(DEVICE_ID) if DEVICE_ID else None

LIGHT_PIN = int(os.getenv("LIGHT_PIN", "20"))
LIGHT_PIN2 = int(os.getenv("LIGHT_PIN2", "25"))
FAN_ENB_PIN = int(os.getenv("FAN_ENB_PIN", "18"))
FAN_ENA_PIN = int(os.getenv("FAN_ENA_PIN", "12"))
FAN_IN1_PIN = int(os.getenv("FAN_IN1_PIN", "5"))
FAN_IN2_PIN = int(os.getenv("FAN_IN2_PIN", "6"))
FAN_IN3_PIN = int(os.getenv("FAN_IN3_PIN", "13"))
FAN_IN4_PIN = int(os.getenv("FAN_IN4_PIN", "19"))
DOOR_PIN = int(os.getenv("DOOR_PIN", "17"))
DOOR_OPEN_SECONDS = float(os.getenv("DOOR_OPEN_SECONDS", "3"))
DOOR_OPEN_ANGLE = float(os.getenv("DOOR_OPEN_ANGLE", "130"))
DOOR_CLOSE_ANGLE = float(os.getenv("DOOR_CLOSE_ANGLE", "0"))
DOOR_SERVO_HOLD_SECONDS = float(os.getenv("DOOR_SERVO_HOLD_SECONDS", "1.2"))
DOOR_SERVO_RELEASE_AFTER_MOVE = os.getenv("DOOR_SERVO_RELEASE_AFTER_MOVE", "1").strip().lower() in {"1", "true", "yes", "on"}
SERVO_MIN_DUTY = float(os.getenv("SERVO_MIN_DUTY", "2.5"))
SERVO_MAX_DUTY = float(os.getenv("SERVO_MAX_DUTY", "12.5"))
SERVO_FREQUENCY = float(os.getenv("SERVO_FREQUENCY", "50"))
DHT_PIN = int(os.getenv("DHT_PIN", "4"))
DHT_TYPE = os.getenv("DHT_TYPE", "11")
# Default ultrasonic pins moved to avoid collision with FAN_IN3/FAN_IN4.
TRIG_PIN = int(os.getenv("TRIG_PIN", "23"))
ECHO_PIN = int(os.getenv("ECHO_PIN", "24"))
DISTANCE_ALERT_CM = float(os.getenv("DISTANCE_ALERT_CM", "20"))
DEVICE_LOOP_INTERVAL = float(os.getenv("DEVICE_LOOP_INTERVAL", "3"))
DISTANCE_LIGHT_PIN = int(os.getenv("DISTANCE_LIGHT_PIN", "22"))
GAS_PIN = int(os.getenv("GAS_PIN", "27"))
FLAME_PIN = int(os.getenv("FLAME_PIN", "14"))
BUZZER_PIN = int(os.getenv("BUZZER_PIN", "16"))
RAIN_PIN = int(os.getenv("RAIN_PIN", "21"))
RAIN_ACTIVE_LOW = os.getenv("RAIN_ACTIVE_LOW", "1").strip().lower() in {"1", "true", "yes", "on"}
RAIN_LOG_INTERVAL_SECONDS = float(os.getenv("RAIN_LOG_INTERVAL_SECONDS", "30"))
RAIN_SERVO_PIN = int(os.getenv("RAIN_SERVO_PIN", "26"))
RAIN_SERVO_DRY_ANGLE = float(os.getenv("RAIN_SERVO_DRY_ANGLE", "0"))
RAIN_SERVO_WET_ANGLE = float(os.getenv("RAIN_SERVO_WET_ANGLE", "180"))
RAIN_SERVO_HOLD_SECONDS = float(os.getenv("RAIN_SERVO_HOLD_SECONDS", "0.6"))
RAIN_SERVO_ENABLED = os.getenv("RAIN_SERVO_ENABLED", "1").strip().lower() in {"1", "true", "yes", "on"}
BUTTON_LIGHT_LIVING_PIN = int(os.getenv("BUTTON_LIGHT_LIVING_PIN", "11"))
BUTTON_FAN_LIVING_PIN = int(os.getenv("BUTTON_FAN_LIVING_PIN", "9"))
BUTTON_LIGHT_BEDROOM_PIN = int(os.getenv("BUTTON_LIGHT_BEDROOM_PIN", "3"))
BUTTON_FAN_BEDROOM_PIN = int(os.getenv("BUTTON_FAN_BEDROOM_PIN", "2"))
BUTTON_ACTIVE_LOW = os.getenv("BUTTON_ACTIVE_LOW", "1").strip().lower() in {"1", "true", "yes", "on"}
BUTTON_DEBOUNCE_SECONDS = float(os.getenv("BUTTON_DEBOUNCE_SECONDS", "0.2"))
BUTTON_POLL_INTERVAL_SECONDS = float(os.getenv("BUTTON_POLL_INTERVAL_SECONDS", "0.05"))
LIGHT_RELAY_ACTIVE_LOW = os.getenv("LIGHT_RELAY_ACTIVE_LOW", "1").strip().lower() in {"1", "true", "yes", "on"}
LIGHT2_RELAY_ACTIVE_LOW = os.getenv("LIGHT2_RELAY_ACTIVE_LOW", "1").strip().lower() in {"1", "true", "yes", "on"}
DISTANCE_LIGHT_ACTIVE_LOW = os.getenv("DISTANCE_LIGHT_ACTIVE_LOW", "0").strip().lower() in {"1", "true", "yes", "on"}
BUZZER_ACTIVE_LOW = os.getenv("BUZZER_ACTIVE_LOW", "0").strip().lower() in {"1", "true", "yes", "on"}
FLAME_ACTIVE_LOW = os.getenv("FLAME_ACTIVE_LOW", "1").strip().lower() in {"1", "true", "yes", "on"}
FLAME_ALERT_BUZZER = os.getenv("FLAME_ALERT_BUZZER", "1").strip().lower() in {"1", "true", "yes", "on"}

FACE_UPLOAD_URL = os.getenv("FACE_UPLOAD_URL", "http://192.168.1.201:8000/face/upload")
FACE_VERIFY_URL = os.getenv("FACE_VERIFY_URL", "http://192.168.1.201:8000/face/verify")
FACE_MODE = os.getenv("FACE_MODE", "verify").lower()
FACE_VERIFY_COOLDOWN = float(os.getenv("FACE_VERIFY_COOLDOWN", "5"))
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
CAPTURE_TIMEOUT_SECONDS = float(os.getenv("CAPTURE_TIMEOUT_SECONDS", "0.8"))
MIN_FACE_SIZE = int(os.getenv("MIN_FACE_SIZE", "80"))
DETECT_INTERVAL = float(os.getenv("DETECT_INTERVAL", "0.2"))
CAMERA_ISO = int(os.getenv("CAMERA_ISO", "0"))
CAMERA_SHUTTER_US = int(os.getenv("CAMERA_SHUTTER_US", "0"))
CAMERA_EXPOSURE_MODE = os.getenv("CAMERA_EXPOSURE_MODE", "auto")
CAMERA_AWB_MODE = os.getenv("CAMERA_AWB_MODE", "auto")
CAMERA_EXPOSURE_COMPENSATION = int(os.getenv("CAMERA_EXPOSURE_COMPENSATION", "10"))
CAMERA_METER_MODE = os.getenv("CAMERA_METER_MODE", "backlit")
CAMERA_DRC_STRENGTH = os.getenv("CAMERA_DRC_STRENGTH", "medium")
CAMERA_BRIGHTNESS = int(os.getenv("CAMERA_BRIGHTNESS", "56"))
CAMERA_CONTRAST = int(os.getenv("CAMERA_CONTRAST", "4"))
CAMERA_SATURATION = int(os.getenv("CAMERA_SATURATION", "2"))
CAMERA2_EXPOSURE_VALUE = float(os.getenv("CAMERA2_EXPOSURE_VALUE", "1.2"))
CAMERA2_SETTLE_SECONDS = float(os.getenv("CAMERA2_SETTLE_SECONDS", "0.6"))
CAMERA2_NOISE_REDUCTION_MODE = int(os.getenv("CAMERA2_NOISE_REDUCTION_MODE", "2"))
CAMERA_BACKEND = os.getenv("CAMERA_BACKEND", "auto").strip().lower()
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "1").strip().lower() in {"1", "true", "yes", "on"}
FAN_PWM_FREQUENCY = float(os.getenv("FAN_PWM_FREQUENCY", "100"))
FAN_WEAK_DUTY = float(os.getenv("FAN_WEAK_DUTY", "45"))
FAN_STRONG_DUTY = float(os.getenv("FAN_STRONG_DUTY", "100"))

state = {
    "den_khach": "off",
    "den_ngu": "off",
    "quat_khach": "off",
    "quat_ngu": "off",
    "temperature_c": None,
    "humidity": None,
    "distance_cm": None,
    "distance_alert": None,
    "distance_light": "off",
    "gas_detected": False,
    "flame_detected": False,
    "buzzer": "off",
    "rain_detected": False,
    "rain_servo_position": None,
    "rain_servo_angle": None,
    "door": "closed",
}


def _resolve_device_map_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return path
    return os.path.join(os.path.dirname(__file__), path)


def load_device_map():
    path = _resolve_device_map_path(DEVICE_MAP_PATH)
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except Exception:
        return {}

    if isinstance(raw, list):
        result = {}
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            device_id = entry.get("id") or entry.get("device_id")
            if device_id:
                result[str(device_id)] = entry
        return result
    if isinstance(raw, dict):
        return {str(key): value for key, value in raw.items() if isinstance(value, dict)}
    return {}


def get_device_registry():
    global DEVICE_REGISTRY
    if DEVICE_REGISTRY is None:
        DEVICE_REGISTRY = load_device_map()
        if not DEVICE_REGISTRY and DEVICE_ID:
            DEVICE_REGISTRY = {DEVICE_ID: {"kind": "gateway"}}
    return DEVICE_REGISTRY


def get_door_device_id():
    if DOOR_DEVICE_ID:
        return DOOR_DEVICE_ID
    registry = get_device_registry()
    for device_id, info in registry.items():
        if str(info.get("kind", "")).lower() == "door":
            return device_id
    return DEVICE_ID or HOME_ID


def build_device_command_topic(device_id):
    return "device/{}/command".format(device_id)


def build_device_status_topic(device_id):
    return "device/{}/status".format(device_id)


def build_device_face_topic(device_id):
    return "device/{}/face".format(device_id)


def build_home_face_topic(home_id):
    return "home/{}/face".format(home_id)


def _normalize_fan_speed(value):
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"low", "weak", "yeu"}:
        return "weak"
    if text in {"high", "strong", "manh", "max"}:
        return "strong"
    if text in {"off", "0", "false"}:
        return "off"
    return text


def apply_device_command(device_id, command, value=None):
    info = get_device_registry().get(device_id, {})
    kind = str(info.get("kind", "")).lower()
    room = str(info.get("room", "")).lower()
    cmd = str(command).strip().lower() if command is not None else ""
    log(
        "apply_device_command device_id={} kind={} room={} command={} value={}".format(
            device_id,
            kind,
            room,
            cmd,
            value,
        )
    )

    if cmd == "toggle" and isinstance(value, bool):
        cmd = "turn_on" if value else "turn_off"

    if kind == "light":
        if cmd in {"turn_on", "on"}:
            set_light_device(room, True)
        elif cmd in {"turn_off", "off"}:
            set_light_device(room, False)
        elif cmd == "toggle":
            is_on = state["den_khach"] == "on" if room == "khach" else state["den_ngu"] == "on"
            set_light_device(room, not is_on)
        return

    if kind == "fan":
        if cmd in {"turn_off", "off"}:
            set_fan_device(room, "off")
            return
        if cmd in {"turn_on", "on"}:
            set_fan_device(room, "strong")
            return
        if cmd == "toggle":
            current = state["quat_khach"] if room == "khach" else state["quat_ngu"]
            set_fan_device(room, "off" if current != "off" else "strong")
            return
        if cmd in {"set_speed", "set_fan_speed"}:
            speed = _normalize_fan_speed(value)
            if speed in {"off", "weak", "strong"}:
                set_fan_device(room, speed)
        elif cmd in {"weak", "strong"}:
            set_fan_device(room, cmd)
        return

    if kind == "door":
        if cmd in {"open", "door_open"}:
            _open_door_async()
        elif cmd in {"close", "door_close"}:
            close_door()
        return

    if kind == "buzzer":
        if cmd in {"turn_on", "on"}:
            set_buzzer_state(True)
        elif cmd in {"turn_off", "off"}:
            set_buzzer_state(False)
        elif cmd == "toggle":
            set_buzzer_state(state["buzzer"] != "on")
        return

    if kind == "distance_light":
        if cmd in {"turn_on", "on"}:
            set_distance_light_state(True)
        elif cmd in {"turn_off", "off"}:
            set_distance_light_state(False)
        elif cmd == "toggle":
            set_distance_light_state(state["distance_light"] != "on")
        return

    if kind == "rain_servo":
        if cmd in {"open", "close"}:
            set_rain_servo_by_weather(cmd == "open")
        elif cmd in {"set_angle", "angle"}:
            try:
                angle = float(value)
            except (TypeError, ValueError):
                angle = None
            if angle is not None:
                set_rain_servo_angle(angle)
        elif cmd in {"set_position", "set_weather"}:
            position = str(value).strip().lower() if value is not None else ""
            if position in {"wet", "rain"}:
                set_rain_servo_by_weather(True)
            elif position in {"dry", "clear"}:
                set_rain_servo_by_weather(False)
        return


def build_device_status_payload(device_id, info):
    kind = str(info.get("kind", "")).lower()
    room = str(info.get("room", "")).lower()
    payload = {
        "online": True,
        "timestamp": int(time.time()),
    }

    if kind == "light":
        is_on = state["den_khach"] == "on" if room == "khach" else state["den_ngu"] == "on"
        payload["status"] = is_on
        payload["metadata"] = {"state": "on" if is_on else "off"}
    elif kind == "fan":
        speed = state["quat_khach"] if room == "khach" else state["quat_ngu"]
        payload["status"] = speed != "off"
        payload["metadata"] = {"speed": speed}
    elif kind == "door":
        is_open = state["door"] == "open"
        payload["status"] = is_open
        payload["metadata"] = {"door": state["door"]}
    elif kind == "buzzer":
        is_on = state["buzzer"] == "on"
        payload["status"] = is_on
        payload["metadata"] = {"buzzer": state["buzzer"]}
    elif kind == "distance_light":
        is_on = state["distance_light"] == "on"
        payload["status"] = is_on
        payload["metadata"] = {"distance_light": state["distance_light"]}
    elif kind == "temperature_humidity":
        payload["status"] = True
        payload["metadata"] = {
            "temperature": state["temperature_c"],
            "humidity": state["humidity"],
        }
    elif kind == "distance_sensor":
        payload["status"] = bool(state["distance_alert"]) if state["distance_alert"] is not None else False
        payload["metadata"] = {
            "distance_cm": state["distance_cm"],
            "distance_alert": state["distance_alert"],
        }
    elif kind == "gas_sensor":
        payload["status"] = bool(state["gas_detected"])
        payload["metadata"] = {"gas_detected": state["gas_detected"]}
    elif kind == "rain_sensor":
        payload["status"] = bool(state["rain_detected"])
        payload["metadata"] = {"rain_detected": state["rain_detected"]}
    elif kind == "rain_servo":
        payload["status"] = True
        payload["metadata"] = {
            "position": state["rain_servo_position"],
            "angle": state["rain_servo_angle"],
        }
    else:
        payload["status"] = False
        payload["metadata"] = {"state": "unknown"}

    return payload


def publish_device_statuses(client):
    registry = get_device_registry()
    for device_id, info in registry.items():
        payload = build_device_status_payload(device_id, info)
        client.publish(build_device_status_topic(device_id), json.dumps(payload), qos=1, retain=False)

stop_event = threading.Event()
face_queue = queue.Queue(maxsize=2)
last_verify_ts = 0.0
door_lock = threading.Lock()
door_pwm = None
fan_khach_pwm = None
fan_ngu_pwm = None
rain_servo_pwm = None
last_rain_log_ts = 0.0
last_button_state = {}
last_button_press_ts = {}
prev_door_state = None  # Track previous door state for logging changes
# Thread used to keep door open while hazardous conditions persist
safety_open_thread = None


def log(message):
    print("[IOT] {}".format(message))


def _log_door_state_change(new_state):
    """Log when door state changes with timestamp and details."""
    global prev_door_state
    if prev_door_state != new_state:
        log("DOOR STATUS CHANGED: {} -> {} (timestamp: {})".format(
            prev_door_state or "unknown",
            new_state,
            time.strftime("%Y-%m-%d %H:%M:%S")
        ))
        prev_door_state = new_state


def _is_output_active_low(pin):
    if pin == LIGHT_PIN:
        return LIGHT_RELAY_ACTIVE_LOW
    if pin == LIGHT_PIN2:
        return LIGHT2_RELAY_ACTIVE_LOW
    if pin == DISTANCE_LIGHT_PIN:
        return DISTANCE_LIGHT_ACTIVE_LOW
    if pin == BUZZER_PIN:
        return BUZZER_ACTIVE_LOW
    return False


def _output_level_for_state(pin, is_on):
    active_low = _is_output_active_low(pin)
    if is_on:
        return GPIO.LOW if active_low else GPIO.HIGH
    return GPIO.HIGH if active_low else GPIO.LOW


def init_gpio():
    if GPIO is None:
        log("RPi.GPIO not available; running in simulation mode.")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LIGHT_PIN, GPIO.OUT)
    GPIO.setup(LIGHT_PIN2, GPIO.OUT)
    GPIO.setup(FAN_ENA_PIN, GPIO.OUT)
    GPIO.setup(FAN_ENB_PIN, GPIO.OUT)
    GPIO.setup(FAN_IN1_PIN, GPIO.OUT)
    GPIO.setup(FAN_IN2_PIN, GPIO.OUT)
    GPIO.setup(FAN_IN3_PIN, GPIO.OUT)
    GPIO.setup(FAN_IN4_PIN, GPIO.OUT)
    GPIO.setup(DOOR_PIN, GPIO.OUT)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.setup(DISTANCE_LIGHT_PIN, GPIO.OUT)
    GPIO.setup(GAS_PIN, GPIO.IN)
    GPIO.setup(FLAME_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP if FLAME_ACTIVE_LOW else GPIO.PUD_DOWN)
    GPIO.setup(RAIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP if RAIN_ACTIVE_LOW else GPIO.PUD_DOWN)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.setup(
        BUTTON_LIGHT_LIVING_PIN,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP if BUTTON_ACTIVE_LOW else GPIO.PUD_DOWN,
    )
    GPIO.setup(
        BUTTON_FAN_LIVING_PIN,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP if BUTTON_ACTIVE_LOW else GPIO.PUD_DOWN,
    )
    GPIO.setup(
        BUTTON_LIGHT_BEDROOM_PIN,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP if BUTTON_ACTIVE_LOW else GPIO.PUD_DOWN,
    )
    GPIO.setup(
        BUTTON_FAN_BEDROOM_PIN,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP if BUTTON_ACTIVE_LOW else GPIO.PUD_DOWN,
    )
    if RAIN_SERVO_ENABLED:
        GPIO.setup(RAIN_SERVO_PIN, GPIO.OUT)
    GPIO.output(LIGHT_PIN, _output_level_for_state(LIGHT_PIN, False))
    GPIO.output(LIGHT_PIN2, _output_level_for_state(LIGHT_PIN2, False))
    GPIO.output(FAN_ENA_PIN, GPIO.LOW)
    GPIO.output(FAN_ENB_PIN, GPIO.LOW)
    GPIO.output(FAN_IN1_PIN, GPIO.LOW)
    GPIO.output(FAN_IN2_PIN, GPIO.LOW)
    GPIO.output(FAN_IN3_PIN, GPIO.LOW)
    GPIO.output(FAN_IN4_PIN, GPIO.LOW)
    GPIO.output(DOOR_PIN, GPIO.LOW)
    GPIO.output(TRIG_PIN, GPIO.LOW)
    GPIO.output(DISTANCE_LIGHT_PIN, _output_level_for_state(DISTANCE_LIGHT_PIN, False))
    GPIO.output(BUZZER_PIN, _output_level_for_state(BUZZER_PIN, False))
    if RAIN_SERVO_ENABLED:
        GPIO.output(RAIN_SERVO_PIN, GPIO.LOW)

    last_button_state.update(
        {
            "light_living": GPIO.input(BUTTON_LIGHT_LIVING_PIN),
            "fan_living": GPIO.input(BUTTON_FAN_LIVING_PIN),
            "light_bedroom": GPIO.input(BUTTON_LIGHT_BEDROOM_PIN),
            "fan_bedroom": GPIO.input(BUTTON_FAN_BEDROOM_PIN),
        }
    )
    last_button_press_ts.update(
        {
            "light_living": 0.0,
            "fan_living": 0.0,
            "light_bedroom": 0.0,
            "fan_bedroom": 0.0,
        }
    )


def set_output(pin, is_on):
    if GPIO is None:
        return
    GPIO.output(pin, _output_level_for_state(pin, is_on))


def _fan_pwm_for(room):
    if room == "khach":
        return fan_khach_pwm
    return fan_ngu_pwm


def _set_fan_direction(room, forward):
    if GPIO is None:
        return
    if room == "khach":
        GPIO.output(FAN_IN1_PIN, GPIO.HIGH if forward else GPIO.LOW)
        GPIO.output(FAN_IN2_PIN, GPIO.LOW if forward else GPIO.HIGH)
    else:
        GPIO.output(FAN_IN3_PIN, GPIO.HIGH if forward else GPIO.LOW)
        GPIO.output(FAN_IN4_PIN, GPIO.LOW if forward else GPIO.HIGH)


def _stop_fan_direction(room):
    if GPIO is None:
        return
    if room == "khach":
        GPIO.output(FAN_IN1_PIN, GPIO.LOW)
        GPIO.output(FAN_IN2_PIN, GPIO.LOW)
    else:
        GPIO.output(FAN_IN3_PIN, GPIO.LOW)
        GPIO.output(FAN_IN4_PIN, GPIO.LOW)


def set_light_device(room, is_on):
    if room == "khach":
        state["den_khach"] = "on" if is_on else "off"
        set_output(LIGHT_PIN, is_on)
    else:
        state["den_ngu"] = "on" if is_on else "off"
        set_output(LIGHT_PIN2, is_on)


def set_fan_device(room, mode):
    pwm = _fan_pwm_for(room)
    normalized = mode.strip().lower()
    if normalized in {"on", "max", "manh"}:
        normalized = "strong"
    if normalized in {"low", "yeu"}:
        normalized = "weak"
    if normalized not in {"off", "weak", "strong"}:
        return

    state_key = "quat_khach" if room == "khach" else "quat_ngu"
    state[state_key] = normalized

    if GPIO is None:
        return

    if pwm is not None:
        if normalized == "off":
            pwm.ChangeDutyCycle(0)
            _stop_fan_direction(room)
        elif normalized == "weak":
            _set_fan_direction(room, True)
            pwm.ChangeDutyCycle(FAN_WEAK_DUTY)
        else:
            _set_fan_direction(room, True)
            pwm.ChangeDutyCycle(FAN_STRONG_DUTY)
    else:
        if normalized == "off":
            _stop_fan_direction(room)
        else:
            _set_fan_direction(room, True)


def set_buzzer_state(is_on):
    state["buzzer"] = "on" if is_on else "off"
    set_output(BUZZER_PIN, is_on)


def read_rain():
    global last_rain_log_ts
    if GPIO is None:
        return

    raw_value = GPIO.input(RAIN_PIN)
    rain_detected = raw_value == GPIO.LOW if RAIN_ACTIVE_LOW else raw_value == GPIO.HIGH
    prev_rain_detected = state["rain_detected"]
    state["rain_detected"] = rain_detected

    if rain_detected != prev_rain_detected:
        set_rain_servo_by_weather(rain_detected)

    now = time.monotonic()
    should_log_periodic = (now - last_rain_log_ts) >= RAIN_LOG_INTERVAL_SECONDS
    if rain_detected != prev_rain_detected:
        log(
            "read_rain: state changed -> {} (raw={}, pin={}, active_low={})".format(
                "RAIN DETECTED" if rain_detected else "DRY",
                raw_value,
                RAIN_PIN,
                RAIN_ACTIVE_LOW,
            )
        )
        last_rain_log_ts = now
    elif should_log_periodic:
        log(
            "read_rain: {} (raw={}, pin={}, active_low={})".format(
                "RAIN DETECTED" if rain_detected else "DRY",
                raw_value,
                RAIN_PIN,
                RAIN_ACTIVE_LOW,
            )
        )
        last_rain_log_ts = now


def _button_pressed(value):
    return value == GPIO.LOW if BUTTON_ACTIVE_LOW else value == GPIO.HIGH


def read_buttons():
    if GPIO is None:
        return False

    now = time.monotonic()
    changed = False
    readings = {
        "light_living": GPIO.input(BUTTON_LIGHT_LIVING_PIN),
        "fan_living": GPIO.input(BUTTON_FAN_LIVING_PIN),
        "light_bedroom": GPIO.input(BUTTON_LIGHT_BEDROOM_PIN),
        "fan_bedroom": GPIO.input(BUTTON_FAN_BEDROOM_PIN),
    }

    for name, value in readings.items():
        prev = last_button_state.get(name)
        last_button_state[name] = value
        if prev is None:
            continue
        if not _button_pressed(value) or _button_pressed(prev):
            continue
        last_ts = last_button_press_ts.get(name, 0.0)
        if (now - last_ts) < BUTTON_DEBOUNCE_SECONDS:
            continue
        last_button_press_ts[name] = now

        if name == "light_living":
            log("@@@@ button GPIO {} pressed: den khach @@@@".format(BUTTON_LIGHT_LIVING_PIN))
            set_light_device("khach", state["den_khach"] != "on")
            changed = True
        elif name == "fan_living":
            log("@@@@ button GPIO {} pressed: quat khach @@@@".format(BUTTON_FAN_LIVING_PIN))
            set_fan_device("khach", "off" if state["quat_khach"] != "off" else "strong")
            changed = True
        elif name == "light_bedroom":
            log("@@@@ button GPIO {} pressed: den ngu @@@@".format(BUTTON_LIGHT_BEDROOM_PIN))
            set_light_device("ngu", state["den_ngu"] != "on")
            changed = True
        elif name == "fan_bedroom":
            log("@@@@ button GPIO {} pressed: quat ngu @@@@".format(BUTTON_FAN_BEDROOM_PIN))
            set_fan_device("ngu", "off" if state["quat_ngu"] != "off" else "strong")
            changed = True

    return changed


def set_distance_light_state(is_on):
    state["distance_light"] = "on" if is_on else "off"
    set_output(DISTANCE_LIGHT_PIN, is_on)


def angle_to_duty(angle, max_angle=180.0):
    safe_max_angle = max(1.0, float(max_angle))
    safe_angle = max(0.0, min(safe_max_angle, angle))
    span = SERVO_MAX_DUTY - SERVO_MIN_DUTY
    return SERVO_MIN_DUTY + (safe_angle / safe_max_angle) * span


def set_rain_servo_by_weather(rain_detected):
    target_angle = RAIN_SERVO_DRY_ANGLE if rain_detected else RAIN_SERVO_WET_ANGLE
    state["rain_servo_position"] = "wet" if rain_detected else "dry"
    state["rain_servo_angle"] = float(target_angle)
    if GPIO is None or rain_servo_pwm is None:
        log("rain_servo: simulation {} deg (rain_detected={})".format(target_angle, rain_detected))
        return

    duty = angle_to_duty(target_angle, max_angle=190.0)
    rain_servo_pwm.ChangeDutyCycle(duty)
    time.sleep(RAIN_SERVO_HOLD_SECONDS)
    rain_servo_pwm.ChangeDutyCycle(0)
    log("rain_servo: set {} deg (rain_detected={})".format(target_angle, rain_detected))


def set_rain_servo_angle(angle, hold_seconds=None):
    if hold_seconds is None:
        hold_seconds = RAIN_SERVO_HOLD_SECONDS
    try:
        numeric_angle = float(angle)
    except (TypeError, ValueError):
        numeric_angle = None
    if numeric_angle is not None:
        state["rain_servo_angle"] = numeric_angle
        state["rain_servo_position"] = None
    if GPIO is None or rain_servo_pwm is None:
        log("rain_servo: simulation {} deg".format(angle))
        return

    duty = angle_to_duty(angle, max_angle=190.0)
    rain_servo_pwm.ChangeDutyCycle(duty)
    time.sleep(hold_seconds)
    rain_servo_pwm.ChangeDutyCycle(0)
    log("rain_servo: set {} deg (manual)".format(angle))


def set_door_angle(angle, hold_seconds=None):
    if hold_seconds is None:
        hold_seconds = DOOR_SERVO_HOLD_SECONDS
    if GPIO is None or door_pwm is None:
        return
    duty = angle_to_duty(angle)
    log(
        "door_servo: pin={} angle={} duty={:.2f} hold={} release={}".format(
            DOOR_PIN,
            angle,
            duty,
            hold_seconds,
            DOOR_SERVO_RELEASE_AFTER_MOVE,
        )
    )
    door_pwm.ChangeDutyCycle(duty)
    time.sleep(hold_seconds)
    if DOOR_SERVO_RELEASE_AFTER_MOVE:
        door_pwm.ChangeDutyCycle(0)


def close_door():
    old_state = state["door"]
    state["door"] = "closed"
    _log_door_state_change("closed")
    if GPIO is None:
        log("door_close: simulation {} deg".format(DOOR_CLOSE_ANGLE))
        return
    set_door_angle(DOOR_CLOSE_ANGLE)
    log("door_close: {} deg".format(DOOR_CLOSE_ANGLE))


def publish_status(client):
    log("publish_status flame_detected={}".format(state["flame_detected"]))
    payload = {
        "den_khach": state["den_khach"],
        "den_ngu": state["den_ngu"],
        "quat_khach": state["quat_khach"],
        "quat_ngu": state["quat_ngu"],
        # Backend expects a boolean-like status field; use overall "any light/fan on" as gateway status.
        "status": bool(
            state["den_khach"] == "on"
            or state["den_ngu"] == "on"
            or state["quat_khach"] != "off"
            or state["quat_ngu"] != "off"
        ),
        "online": True,
        # Backward compatibility fields.
        "light": "on" if state["den_khach"] == "on" or state["den_ngu"] == "on" else "off",
        "fan": "on" if state["quat_khach"] != "off" or state["quat_ngu"] != "off" else "off",
        # Map to keys the backend understands in metadata.
        "temperature": state["temperature_c"],
        "humidity": state["humidity"],
        "distance_light": state["distance_light"],
        "gas_detected": state["gas_detected"],
        "flame_detected": state["flame_detected"],
        "buzzer": state["buzzer"],
        "rain_detected": state["rain_detected"],
        "rain_servo_position": state["rain_servo_position"],
        "rain_servo_angle": state["rain_servo_angle"],
        "door": state["door"],
        "timestamp": int(time.time()),
    }
    # Also publish legacy status for older consumers, if any.
    client.publish(LEGACY_STATUS_TOPIC, json.dumps(payload), qos=1, retain=False)


def publish_sensors(client):
    log("publish_sensors")
    payload = {
        "distance_cm": state["distance_cm"],
        "distance_alert": state["distance_alert"],
        "distance_light": state["distance_light"],
        "gas_detected": state["gas_detected"],
        "flame_detected": state["flame_detected"],
        "buzzer": state["buzzer"],
        "rain_detected": state["rain_detected"],
        "rain_servo_position": state["rain_servo_position"],
        "rain_servo_angle": state["rain_servo_angle"],
        "timestamp": int(time.time()),
    }
    # Sensors are published on legacy topic only for now.
    client.publish(LEGACY_SENSOR_TOPIC, json.dumps(payload), qos=1, retain=False)


def get_dht_sensor():
    if Adafruit_DHT is None:
        return None
    if DHT_TYPE == "22":
        return Adafruit_DHT.DHT22
    return Adafruit_DHT.DHT11


def read_dht():
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


def read_distance():
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
    state["distance_alert"] = distance_cm < DISTANCE_ALERT_CM
    set_distance_light_state(state["distance_alert"])
    log("read_distance: {}cm alert={}".format(state["distance_cm"], state["distance_alert"]))


def read_gas():
    if GPIO is None:
        return

    gas_detected = GPIO.input(GAS_PIN) == GPIO.HIGH
    state["gas_detected"] = gas_detected
    set_buzzer_state(gas_detected)
    if gas_detected:
        log("read_gas: GAS DETECTED -> buzzer on")
        try:
            _open_door_until_safe()
        except Exception:
            pass
    else:
        log("read_gas: no gas detected -> buzzer off")


def read_flame():
    if GPIO is None:
        return

    raw_value = GPIO.input(FLAME_PIN)
    flame_detected = raw_value == GPIO.LOW if FLAME_ACTIVE_LOW else raw_value == GPIO.HIGH
    prev_flame_detected = state["flame_detected"]
    state["flame_detected"] = flame_detected
    
    if flame_detected != prev_flame_detected:
        if flame_detected and FLAME_ALERT_BUZZER:
            set_buzzer_state(True)
            log("read_flame: FLAME DETECTED -> buzzer on (pin={}, active_low={})".format(FLAME_PIN, FLAME_ACTIVE_LOW))
            try:
                _open_door_until_safe()
            except Exception:
                pass
        elif not flame_detected and not state["gas_detected"] and FLAME_ALERT_BUZZER:
            set_buzzer_state(False)
            log("read_flame: flame no longer detected -> buzzer off")
    
    if flame_detected != prev_flame_detected:
        log("read_flame: state changed -> {} (raw={}, pin={}, active_low={})".format(
            "FLAME DETECTED" if flame_detected else "NO FLAME",
            raw_value,
            FLAME_PIN,
            FLAME_ACTIVE_LOW,
        ))


def _open_door_until_safe():
    """Open the door and keep it open until both flame and gas sensors are clear.

    Runs in a background thread and avoids starting multiple concurrent safety threads.
    """
    global safety_open_thread

    def _worker():
        with door_lock:
            state["door"] = "open"
            _log_door_state_change("open")
            if GPIO is None:
                log("door_open_safety: simulation (waiting until sensors clear)")
            else:
                log("door_open_safety: opening door for safety")
                set_door_angle(DOOR_OPEN_ANGLE)

        try:
            # Wait until both sensors report no hazard or stop_event is set
            while not stop_event.is_set() and (state.get("flame_detected") or state.get("gas_detected")):
                time.sleep(0.5)
        finally:
            # Close the door once safe
            try:
                close_door()
            except Exception as exc:
                log("door_open_safety: error while closing door: {}".format(exc))

    # Avoid starting multiple threads
    if safety_open_thread is not None and safety_open_thread.is_alive():
        return

    safety_open_thread = threading.Thread(target=_worker, daemon=True)
    safety_open_thread.start()


def apply_command(command):
    cmd = command.strip().lower()
    log("apply_command: {}".format(cmd))
    if cmd in {"on", "off", "toggle"}:
        cmd = "den khach {}".format(cmd)

    if cmd in {"light on", "light off", "light toggle"}:
        cmd = cmd.replace("light", "den khach")
    if cmd in {"fan on", "fan off", "fan toggle"}:
        cmd = cmd.replace("fan", "quat khach")

    if cmd in {"den khach on", "denkhach on", "living light on"}:
        set_light_device("khach", True)
        return
    if cmd in {"den khach off", "denkhach off", "living light off"}:
        set_light_device("khach", False)
        return
    if cmd in {"den khach toggle", "denkhach toggle", "living light toggle"}:
        set_light_device("khach", state["den_khach"] != "on")
        return

    if cmd in {"den ngu on", "denngu on", "bedroom light on"}:
        set_light_device("ngu", True)
        return
    if cmd in {"den ngu off", "denngu off", "bedroom light off"}:
        set_light_device("ngu", False)
        return
    if cmd in {"den ngu toggle", "denngu toggle", "bedroom light toggle"}:
        set_light_device("ngu", state["den_ngu"] != "on")
        return

    if cmd in {"quat khach on", "quatkhach on", "living fan on"}:
        set_fan_device("khach", "strong")
        return
    if cmd in {"quat khach off", "quatkhach off", "living fan off"}:
        set_fan_device("khach", "off")
        return
    if cmd in {"quat khach weak", "quat khach yeu", "quatkhach weak", "living fan weak"}:
        set_fan_device("khach", "weak")
        return
    if cmd in {"quat khach strong", "quat khach manh", "quatkhach strong", "living fan strong"}:
        set_fan_device("khach", "strong")
        return
    if cmd in {"quat khach toggle", "quatkhach toggle", "living fan toggle"}:
        set_fan_device("khach", "off" if state["quat_khach"] != "off" else "strong")
        return

    if cmd in {"quat ngu on", "quatngu on", "bedroom fan on"}:
        set_fan_device("ngu", "strong")
        return
    if cmd in {"quat ngu off", "quatngu off", "bedroom fan off"}:
        set_fan_device("ngu", "off")
        return
    if cmd in {"quat ngu weak", "quat ngu yeu", "quatngu weak", "bedroom fan weak"}:
        set_fan_device("ngu", "weak")
        return
    if cmd in {"quat ngu strong", "quat ngu manh", "quatngu strong", "bedroom fan strong"}:
        set_fan_device("ngu", "strong")
        return
    if cmd in {"quat ngu toggle", "quatngu toggle", "bedroom fan toggle"}:
        set_fan_device("ngu", "off" if state["quat_ngu"] != "off" else "strong")
        return

    if cmd == "all on":
        set_light_device("khach", True)
        set_light_device("ngu", True)
        set_fan_device("khach", "strong")
        set_fan_device("ngu", "strong")
        return

    if cmd == "all off":
        set_light_device("khach", False)
        set_light_device("ngu", False)
        set_fan_device("khach", "off")
        set_fan_device("ngu", "off")
        return

    if cmd in {"buzzer on", "buzzer off", "buzzer toggle"}:
        if cmd == "buzzer on":
            set_buzzer_state(True)
        elif cmd == "buzzer off":
            set_buzzer_state(False)
        else:
            set_buzzer_state(state["buzzer"] != "on")
        return

    if cmd in {"door open", "door close"}:
        if cmd == "door open":
            _open_door_async()
        else:
            close_door()
        return

    if cmd in {
        "rain servo open",
        "rain_servo open",
        "rainservo open",
        "sky window open",
        "roof window open",
        "cua so troi open",
        "mai che open",
    }:
        set_rain_servo_by_weather(True)
        return

    if cmd in {
        "rain servo close",
        "rain_servo close",
        "rainservo close",
        "sky window close",
        "roof window close",
        "cua so troi close",
        "mai che close",
    }:
        set_rain_servo_by_weather(False)
        return

    for prefix in ("rain servo angle ", "rain_servo angle ", "rainservo angle "):
        if cmd.startswith(prefix):
            try:
                set_rain_servo_angle(float(cmd[len(prefix):].strip()))
            except ValueError:
                log("rain_servo: invalid angle command '{}'".format(command))
            return

    if cmd == "status":
        return


def _open_door_async():
    if GPIO is None:
        state["door"] = "open"
        _log_door_state_change("open")
        log("door_open: simulation {} deg (will auto-close after {} seconds)".format(
            DOOR_OPEN_ANGLE,
            DOOR_OPEN_SECONDS
        ))
        time.sleep(DOOR_OPEN_SECONDS)
        state["door"] = "closed"
        _log_door_state_change("closed")
        return

    def _rotate() -> None:
        with door_lock:
            state["door"] = "open"
            _log_door_state_change("open")
            log("door_open: {} deg (face verification success - will auto-close after {} seconds)".format(
                DOOR_OPEN_ANGLE,
                DOOR_OPEN_SECONDS
            ))
            set_door_angle(DOOR_OPEN_ANGLE)
            time.sleep(DOOR_OPEN_SECONDS)
            close_door()

    threading.Thread(target=_rotate, daemon=True).start()


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        log("mqtt connected")
        # Subscribe to all configured device command topics.
        registry = get_device_registry()
        for device_id in registry.keys():
            client.subscribe(build_device_command_topic(device_id), qos=1)
        client.subscribe(LEGACY_COMMAND_TOPIC, qos=1)
        publish_device_statuses(client)
        publish_status(client)
    else:
        log("MQTT connect failed: {}".format(rc))


def on_message(client, userdata, msg):
    try:
        raw = msg.payload.decode("utf-8")
    except UnicodeDecodeError:
        log("Invalid command payload")
        return

    log("-------------------------------------------")
    log("raw command: {}".format(raw))
    log("-------------------------------------------")

    topic = msg.topic
    device_id = None
    if topic.startswith("device/"):
        parts = topic.split("/")
        if len(parts) == 3 and parts[2] == "command":
            device_id = parts[1]

    command_to_apply = raw
    # New backend commands are JSON: {"command": "...", "value": ...}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "command" in parsed:
            cmd = str(parsed.get("command", "")).strip()
            value = parsed.get("value")
            if device_id:
                apply_device_command(device_id, cmd, value)
                publish_device_statuses(client)
                return
            if cmd == "toggle":
                # Default mapping: toggle the living room light based on boolean value.
                if isinstance(value, bool):
                    command_to_apply = "den khach on" if value else "den khach off"
                else:
                    command_to_apply = "den khach toggle"
            elif cmd in {"door", "door_open"}:
                command_to_apply = "door open"
            elif cmd in {"door_close"}:
                command_to_apply = "door close"
            else:
                # Fallback: treat as free-form command string.
                command_to_apply = cmd if value is None else "{} {}".format(cmd, value)
    except Exception:
        pass

    if device_id:
        apply_device_command(device_id, command_to_apply, None)
        publish_device_statuses(client)
        return

    apply_command(command_to_apply)
    publish_device_statuses(client)
    publish_status(client)
    log(
        "Command '{}' applied. DenKhach={}, DenNgu={}, QuatKhach={}, QuatNgu={}, FlameDetected={}.".format(
            command_to_apply,
            state["den_khach"],
            state["den_ngu"],
            state["quat_khach"],
            state["quat_ngu"],
            state["flame_detected"],
        )
    )


def build_mqtt_client():
    if mqtt is None:
        log("paho-mqtt not available; MQTT disabled.")
        return None

    masked_password = "***" if MQTT_PASSWORD else ""
    log(
        "mqtt config host={} port={} tls={} username={} password={}".format(
            BROKER_HOST,
            BROKER_PORT,
            MQTT_USE_TLS,
            MQTT_USERNAME or "",
            masked_password,
        )
    )
    client = mqtt.Client(client_id="home-{}".format(HOME_ID))
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    if MQTT_USE_TLS or BROKER_PORT == 8883:
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        log("mqtt tls enabled for {}:{}".format(BROKER_HOST, BROKER_PORT))

    client.on_connect = on_connect
    client.on_message = on_message
    log("mqtt connect -> {}:{} topics cmd={} legacy_status={} legacy_sensor={}".format(
        BROKER_HOST,
        BROKER_PORT,
        ",".join([build_device_command_topic(d) for d in get_device_registry().keys()])
        if get_device_registry()
        else (DEVICE_COMMAND_TOPIC or LEGACY_COMMAND_TOPIC),
        LEGACY_STATUS_TOPIC,
        LEGACY_SENSOR_TOPIC,
    ))
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
        client.loop_start()
        return client
    except Exception as exc:
        log("mqtt connect failed: {}. Running without MQTT.".format(exc))
        return None


def _set_picamera2_controls_safe(camera2, controls):
    for key, value in controls.items():
        try:
            camera2.set_controls({key: value})
        except Exception as exc:
            log("picamera2 control '{}' skipped: {}".format(key, exc))


def capture_face_jpeg(
    camera_index=0,
    timeout_seconds=0.2,
    jpeg_quality=85,
):
    if cv2 is None:
        raise RuntimeError("OpenCV is not installed")

    if CAMERA_BACKEND in {"auto", "picamera2", "libcamera"} and Picamera2 is not None:
        log("capture: picamera2")
        camera2 = Picamera2()
        try:
            config = camera2.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"},
                controls={"AeEnable": True, "AwbEnable": True},
            )
            camera2.configure(config)
            camera2.start()
            _set_picamera2_controls_safe(
                camera2,
                {
                    "ExposureValue": CAMERA2_EXPOSURE_VALUE,
                    "NoiseReductionMode": CAMERA2_NOISE_REDUCTION_MODE,
                },
            )
            time.sleep(CAMERA2_SETTLE_SECONDS)

            deadline = time.monotonic() + timeout_seconds
            while time.monotonic() < deadline:
                frame = camera2.capture_array()
                if frame is None:
                    time.sleep(0.03)
                    continue

                # Picamera2 tr? v? RGB, d?i sang BGR d? x? lÃ½ mÃ u dÃºng trong OpenCV.
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # X? lÃ½ tang sÃ¡ng/cÃ¢n b?ng mÃ u
                frame = enhance_face_image(frame)
                success, buffer = cv2.imencode(
                    ".jpg",
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
                )
                if success:
                    log("capture: picamera2 frame encoded")
                    return buffer.tobytes(), None
                time.sleep(0.03)
        finally:
            try:
                camera2.stop()
            except Exception:
                pass

    if CAMERA_BACKEND in {"auto", "picamera", "legacy"} and PiCamera is not None:
        log("capture: PiCamera")
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 24
        camera.exposure_mode = CAMERA_EXPOSURE_MODE
        camera.awb_mode = CAMERA_AWB_MODE
        camera.exposure_compensation = CAMERA_EXPOSURE_COMPENSATION
        camera.meter_mode = CAMERA_METER_MODE
        camera.drc_strength = CAMERA_DRC_STRENGTH
        camera.brightness = CAMERA_BRIGHTNESS
        camera.contrast = CAMERA_CONTRAST
        camera.saturation = CAMERA_SATURATION
        camera.iso = CAMERA_ISO
        camera.shutter_speed = CAMERA_SHUTTER_US
        raw_capture = PiRGBArray(camera, size=(640, 480))
        time.sleep(1.2)

        try:
            deadline = time.monotonic() + timeout_seconds
            for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
                if time.monotonic() > deadline:
                    return None, None

                image = frame.array
                raw_capture.truncate(0)
                # X? lÃ½ tang sÃ¡ng/cÃ¢n b?ng mÃ u
                image = enhance_face_image(image)
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

            # X? lÃ½ tang sÃ¡ng/cÃ¢n b?ng mÃ u
            frame = enhance_face_image(frame)
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


def enhance_face_image(img):
    # 1) Kh? nhi?u nh?, trÃ¡nh m?t chi ti?t.
    denoised = cv2.GaussianBlur(img, (3, 3), 0)

    # 2) CÃ¢n b?ng tr?ng nh? theo kÃªnh a/b trong LAB.
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    avg_a = float(cv2.mean(a_channel)[0])
    avg_b = float(cv2.mean(b_channel)[0])
    a_channel = cv2.addWeighted(a_channel, 1.0, a_channel, 0.0, -(avg_a - 128.0) * 0.4)
    b_channel = cv2.addWeighted(b_channel, 1.0, b_channel, 0.0, -(avg_b - 128.0) * 0.4)
    wb = cv2.cvtColor(cv2.merge((l_channel, a_channel, b_channel)), cv2.COLOR_LAB2BGR)

    # 2.1) N?u ?nh Ã¡m xanh m?nh thÃ¬ gi?m nh? kÃªnh xanh.
    b_mean, g_mean, r_mean, _ = cv2.mean(wb)
    if g_mean > (r_mean * 1.15) and g_mean > (b_mean * 1.12):
        b_channel, g_channel, r_channel = cv2.split(wb)
        g_channel = cv2.convertScaleAbs(g_channel, alpha=0.9, beta=0)
        wb = cv2.merge((b_channel, g_channel, r_channel))

    # 3) Tang sÃ¡ng/tuong ph?n nh? theo m?c t?i d? trÃ¡nh l?i LUT trÃªn OpenCV cu.
    gray = cv2.cvtColor(wb, cv2.COLOR_BGR2GRAY)
    luminance = float(cv2.mean(gray)[0])
    if luminance < 70:
        alpha = 1.28
        beta = 30
    elif luminance < 95:
        alpha = 1.16
        beta = 18
    else:
        alpha = 1.06
        beta = 8
    bright = cv2.convertScaleAbs(wb, alpha=alpha, beta=beta)

    # 4) NÃ©t nh?, trÃ¡nh halo.
    blur = cv2.GaussianBlur(bright, (0, 0), 0.8)
    return cv2.addWeighted(bright, 1.08, blur, -0.08, 0)


def device_loop(client):
    next_sensor_ts = 0.0
    while not stop_event.is_set():
        now = time.monotonic()
        if now >= next_sensor_ts:
            log("device_loop tick")
            read_dht()
            read_distance()
            read_gas()
            read_flame()
            read_rain()

            if client is not None:
                publish_device_statuses(client)
                publish_status(client)
                publish_sensors(client)
            next_sensor_ts = now + DEVICE_LOOP_INTERVAL

        time.sleep(BUTTON_POLL_INTERVAL_SECONDS)


def button_loop(client):
    log(
        "button_loop start interval={}s debounce={}s".format(
            BUTTON_POLL_INTERVAL_SECONDS,
            BUTTON_DEBOUNCE_SECONDS,
        )
    )
    while not stop_event.is_set():
        button_changed = read_buttons()
        if button_changed and client is not None:
            publish_device_statuses(client)
            publish_status(client)
        time.sleep(BUTTON_POLL_INTERVAL_SECONDS)


def face_capture_loop():
    if cv2 is None:
        log("OpenCV not available; face upload disabled.")
        return

    error_count = 0

    while not stop_event.is_set():
        try:
            image_bytes, _ = capture_face_jpeg(
                camera_index=CAMERA_INDEX,
                timeout_seconds=CAPTURE_TIMEOUT_SECONDS,
            )
            if image_bytes:
                log("face_capture: got image")
                error_count = 0
                if face_queue.full():
                    try:
                        face_queue.get_nowait()
                    except queue.Empty:
                        pass
                face_queue.put(image_bytes)
        except Exception as exc:
            error_count += 1
            if error_count == 1 or error_count % 10 == 0:
                log("Face capture error: {}".format(exc))
            time.sleep(min(5.0, 0.5 * error_count))

        time.sleep(DETECT_INTERVAL)


def publish_face_image(client, action, image_bytes, person_id=None):
    if client is None:
        log("face_mqtt: MQTT client unavailable")
        return False

    door_device_id = get_door_device_id()
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    payload = {
        "home_id": HOME_ID,
        "door_device_id": door_device_id,
        "action": action,
        "image_base64": image_b64,
    }
    if person_id:
        payload["person_id"] = person_id
    topic = build_home_face_topic(HOME_ID)
    info = client.publish(topic, json.dumps(payload), qos=1, retain=False)
    if mqtt is not None and info.rc != mqtt.MQTT_ERR_SUCCESS:
        log("face_mqtt: publish failed rc={}".format(info.rc))
        return False

    log("face_mqtt: published action={} topic={}".format(action, topic))
    return True


def face_send_loop(client):
    global last_verify_ts
    log("face_send_loop start mode={}".format(FACE_MODE))
    if client is None:
        log("face_send_loop: MQTT unavailable; face upload disabled.")
        return

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
                log("face_verify: publishing to mqtt for verification")
                if publish_face_image(client, "verify", image_bytes):
                    last_verify_ts = now
                    log(
                        "face_verify: Face image sent to backend. Waiting for verification result and automatic door unlock..."
                    )
            else:
                log("face_upload: publishing to mqtt")
                publish_face_image(client, "upload", image_bytes)
        except Exception as exc:
            log("Face send error: {}".format(exc))


def main():
    global door_pwm, fan_khach_pwm, fan_ngu_pwm, rain_servo_pwm
    log("iot_client starting")
    init_gpio()
    if GPIO is not None:
        door_pwm = GPIO.PWM(DOOR_PIN, SERVO_FREQUENCY)
        door_pwm.start(0)
        fan_khach_pwm = GPIO.PWM(FAN_ENA_PIN, FAN_PWM_FREQUENCY)
        fan_khach_pwm.start(0)
        fan_ngu_pwm = GPIO.PWM(FAN_ENB_PIN, FAN_PWM_FREQUENCY)
        fan_ngu_pwm.start(0)
        if RAIN_SERVO_ENABLED:
            rain_servo_pwm = GPIO.PWM(RAIN_SERVO_PIN, SERVO_FREQUENCY)
            rain_servo_pwm.start(0)
        set_fan_device("khach", "off")
        set_fan_device("ngu", "off")
        set_light_device("khach", False)
        set_light_device("ngu", False)
        close_door()
        if RAIN_SERVO_ENABLED:
            set_rain_servo_by_weather(False)

    client = build_mqtt_client()

    threads = [
        threading.Thread(target=button_loop, args=(client,), daemon=True),
        threading.Thread(target=device_loop, args=(client,), daemon=True),
        threading.Thread(target=face_capture_loop, daemon=True),
        threading.Thread(target=face_send_loop, args=(client,), daemon=True),
    ]

    for thread in threads:
        thread.start()

    # Initialize door state tracking
    global prev_door_state
    prev_door_state = state["door"]

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        log("iot_client stopping")
        if client is not None:
            client.loop_stop()
        if fan_khach_pwm is not None:
            fan_khach_pwm.stop()
        if fan_ngu_pwm is not None:
            fan_ngu_pwm.stop()
        if rain_servo_pwm is not None:
            rain_servo_pwm.stop()
        if door_pwm is not None:
            door_pwm.stop()
        if GPIO is not None:
            GPIO.cleanup()


if __name__ == "__main__":
    main()
