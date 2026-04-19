import base64
import json
import os
import queue
import ssl
import threading
import time

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

try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None

BROKER_HOST = os.getenv(
    "MQTT_BROKER_HOST",
    "0d847a93f8b9463487a312fdd241108a.s1.eu.hivemq.cloud"
)

BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "8883"))

MQTT_USERNAME = os.getenv("MQTT_USERNAME", "testuser")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "19122005Tri")

HOME_ID = os.getenv("HOME_ID", "home-001")
DEVICE_ID = os.getenv("DEVICE_ID", "raspi-01")


COMMAND_TOPIC = "smarthome/{}/{}/commands".format(HOME_ID, DEVICE_ID)
STATUS_TOPIC = "smarthome/{}/{}/status".format(HOME_ID, DEVICE_ID)
SENSOR_TOPIC = "smarthome/{}/{}/sensors".format(HOME_ID, DEVICE_ID)

LIGHT_PIN = int(os.getenv("LIGHT_PIN", "20"))
LIGHT_PIN2 = int(os.getenv("LIGHT_PIN2", "25"))

# Dual-fan driver (L298N/L293D style):
# - Quat khach: ENA + IN1/IN2
# - Quat ngu:   ENB + IN3/IN4
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
BUZZER_PIN = int(os.getenv("BUZZER_PIN", "16"))
RAIN_PIN = int(os.getenv("RAIN_PIN", "21"))
RAIN_ACTIVE_LOW = os.getenv("RAIN_ACTIVE_LOW", "1").strip().lower() in {"1", "true", "yes", "on"}
RAIN_LOG_INTERVAL_SECONDS = float(os.getenv("RAIN_LOG_INTERVAL_SECONDS", "30"))
RAIN_SERVO_PIN = int(os.getenv("RAIN_SERVO_PIN", "26"))
RAIN_SERVO_DRY_ANGLE = float(os.getenv("RAIN_SERVO_DRY_ANGLE", "0"))
RAIN_SERVO_WET_ANGLE = float(os.getenv("RAIN_SERVO_WET_ANGLE", "190"))
RAIN_SERVO_HOLD_SECONDS = float(os.getenv("RAIN_SERVO_HOLD_SECONDS", "0.6"))
RAIN_SERVO_ENABLED = os.getenv("RAIN_SERVO_ENABLED", "1").strip().lower() in {"1", "true", "yes", "on"}

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
    "buzzer": "off",
    "rain_detected": False,
    "door": "closed",
}

stop_event = threading.Event()
face_queue = queue.Queue(maxsize=2)
last_verify_ts = 0.0
door_lock = threading.Lock()
door_pwm = None
fan_khach_pwm = None
fan_ngu_pwm = None
rain_servo_pwm = None
last_rain_log_ts = 0.0


def log(message):
    print("[IOT] {}".format(message))


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
    GPIO.setup(RAIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP if RAIN_ACTIVE_LOW else GPIO.PUD_DOWN)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    if RAIN_SERVO_ENABLED:
        GPIO.setup(RAIN_SERVO_PIN, GPIO.OUT)
    GPIO.output(LIGHT_PIN, GPIO.LOW)
    GPIO.output(LIGHT_PIN2, GPIO.LOW)
    GPIO.output(FAN_ENA_PIN, GPIO.LOW)
    GPIO.output(FAN_ENB_PIN, GPIO.LOW)
    GPIO.output(FAN_IN1_PIN, GPIO.LOW)
    GPIO.output(FAN_IN2_PIN, GPIO.LOW)
    GPIO.output(FAN_IN3_PIN, GPIO.LOW)
    GPIO.output(FAN_IN4_PIN, GPIO.LOW)
    GPIO.output(DOOR_PIN, GPIO.LOW)
    GPIO.output(TRIG_PIN, GPIO.LOW)
    GPIO.output(DISTANCE_LIGHT_PIN, GPIO.LOW)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    if RAIN_SERVO_ENABLED:
        GPIO.output(RAIN_SERVO_PIN, GPIO.LOW)


def set_output(pin, is_on):
    if GPIO is None:
        return
    GPIO.output(pin, GPIO.HIGH if is_on else GPIO.LOW)


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


def set_distance_light_state(is_on):
    state["distance_light"] = "on" if is_on else "off"
    set_output(DISTANCE_LIGHT_PIN, is_on)


def angle_to_duty(angle, max_angle=180.0):
    safe_max_angle = max(1.0, float(max_angle))
    safe_angle = max(0.0, min(safe_max_angle, angle))
    span = SERVO_MAX_DUTY - SERVO_MIN_DUTY
    return SERVO_MIN_DUTY + (safe_angle / safe_max_angle) * span


def set_rain_servo_by_weather(rain_detected):
    target_angle = RAIN_SERVO_WET_ANGLE if rain_detected else RAIN_SERVO_DRY_ANGLE
    if GPIO is None or rain_servo_pwm is None:
        log("rain_servo: simulation {} deg (rain_detected={})".format(target_angle, rain_detected))
        return

    duty = angle_to_duty(target_angle, max_angle=190.0)
    rain_servo_pwm.ChangeDutyCycle(duty)
    time.sleep(RAIN_SERVO_HOLD_SECONDS)
    rain_servo_pwm.ChangeDutyCycle(0)
    log("rain_servo: set {} deg (rain_detected={})".format(target_angle, rain_detected))


def set_door_angle(angle, hold_seconds=0.5):
    if GPIO is None or door_pwm is None:
        return
    duty = angle_to_duty(angle)
    door_pwm.ChangeDutyCycle(duty)
    time.sleep(hold_seconds)
    door_pwm.ChangeDutyCycle(0)


def close_door():
    state["door"] = "closed"
    if GPIO is None:
        log("door_close: simulation {} deg".format(DOOR_CLOSE_ANGLE))
        return
    set_door_angle(DOOR_CLOSE_ANGLE)
    log("door_close: {} deg".format(DOOR_CLOSE_ANGLE))


def publish_status(client):
    log("publish_status")
    payload = {
        "device_id": DEVICE_ID,
        "den_khach": state["den_khach"],
        "den_ngu": state["den_ngu"],
        "quat_khach": state["quat_khach"],
        "quat_ngu": state["quat_ngu"],
        # Backward compatibility fields.
        "light": "on" if state["den_khach"] == "on" or state["den_ngu"] == "on" else "off",
        "fan": "on" if state["quat_khach"] != "off" or state["quat_ngu"] != "off" else "off",
        "temperature_c": state["temperature_c"],
        "humidity": state["humidity"],
        "distance_light": state["distance_light"],
        "gas_detected": state["gas_detected"],
        "buzzer": state["buzzer"],
        "rain_detected": state["rain_detected"],
        "door": state["door"],
        "timestamp": int(time.time()),
    }
    client.publish(STATUS_TOPIC, json.dumps(payload), qos=1, retain=False)


def publish_sensors(client):
    log("publish_sensors")
    payload = {
        "device_id": DEVICE_ID,
        "distance_cm": state["distance_cm"],
        "distance_alert": state["distance_alert"],
        "distance_light": state["distance_light"],
        "gas_detected": state["gas_detected"],
        "buzzer": state["buzzer"],
        "rain_detected": state["rain_detected"],
        "timestamp": int(time.time()),
    }
    client.publish(SENSOR_TOPIC, json.dumps(payload), qos=1, retain=False)


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
    state["distance_alert"] = distance_cm <= DISTANCE_ALERT_CM
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
    else:
        log("read_gas: no gas detected -> buzzer off")


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

    if cmd == "status":
        return


def _open_door_async():
    if GPIO is None:
        state["door"] = "open"
        log("door_open: simulation {} deg".format(DOOR_OPEN_ANGLE))
        time.sleep(DOOR_OPEN_SECONDS)
        state["door"] = "closed"
        return

    def _rotate() -> None:
        with door_lock:
            state["door"] = "open"
            log("door_open: {} deg".format(DOOR_OPEN_ANGLE))
            set_door_angle(DOOR_OPEN_ANGLE)
            time.sleep(DOOR_OPEN_SECONDS)
            close_door()

    threading.Thread(target=_rotate, daemon=True).start()


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        log("mqtt connected")
        client.subscribe(COMMAND_TOPIC, qos=1)
        publish_status(client)
    else:
        log("MQTT connect failed: {}".format(rc))


def on_message(client, userdata, msg):
    try:
        command = msg.payload.decode("utf-8")
    except UnicodeDecodeError:
        log("Invalid command payload")
        return

    apply_command(command)
    publish_status(client)
    log(
        "Command '{}' applied. DenKhach={}, DenNgu={}, QuatKhach={}, QuatNgu={}.".format(
            command,
            state["den_khach"],
            state["den_ngu"],
            state["quat_khach"],
            state["quat_ngu"],
        )
    )


def build_mqtt_client():
    if mqtt is None:
        log("paho-mqtt not available; MQTT disabled.")
        return None

    client = mqtt.Client(client_id="device-{}".format(DEVICE_ID))
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    if MQTT_USE_TLS or BROKER_PORT == 8883:
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        log("mqtt tls enabled for {}:{}".format(BROKER_HOST, BROKER_PORT))

    client.on_connect = on_connect
    client.on_message = on_message
    log("mqtt connect -> {}:{} topic cmd={} status={} sensor={}".format(
        BROKER_HOST,
        BROKER_PORT,
        COMMAND_TOPIC,
        STATUS_TOPIC,
        SENSOR_TOPIC,
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

                # Picamera2 trả về RGB, đổi sang BGR để xử lý màu đúng trong OpenCV.
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # Xử lý tăng sáng/cân bằng màu
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
                # Xử lý tăng sáng/cân bằng màu
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

            # Xử lý tăng sáng/cân bằng màu
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
    # 1) Khử nhiễu nhẹ, tránh mất chi tiết.
    denoised = cv2.GaussianBlur(img, (3, 3), 0)

    # 2) Cân bằng trắng nhẹ theo kênh a/b trong LAB.
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    avg_a = float(cv2.mean(a_channel)[0])
    avg_b = float(cv2.mean(b_channel)[0])
    a_channel = cv2.addWeighted(a_channel, 1.0, a_channel, 0.0, -(avg_a - 128.0) * 0.4)
    b_channel = cv2.addWeighted(b_channel, 1.0, b_channel, 0.0, -(avg_b - 128.0) * 0.4)
    wb = cv2.cvtColor(cv2.merge((l_channel, a_channel, b_channel)), cv2.COLOR_LAB2BGR)

    # 2.1) Nếu ảnh ám xanh mạnh thì giảm nhẹ kênh xanh.
    b_mean, g_mean, r_mean, _ = cv2.mean(wb)
    if g_mean > (r_mean * 1.15) and g_mean > (b_mean * 1.12):
        b_channel, g_channel, r_channel = cv2.split(wb)
        g_channel = cv2.convertScaleAbs(g_channel, alpha=0.9, beta=0)
        wb = cv2.merge((b_channel, g_channel, r_channel))

    # 3) Tăng sáng/tương phản nhẹ theo mức tối để tránh lỗi LUT trên OpenCV cũ.
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

    # 4) Nét nhẹ, tránh halo.
    blur = cv2.GaussianBlur(bright, (0, 0), 0.8)
    return cv2.addWeighted(bright, 1.08, blur, -0.08, 0)


def device_loop(client):
    while not stop_event.is_set():
        log("device_loop tick")
        read_dht()
        read_distance()
        read_gas()
        read_rain()

        if client is not None:
            publish_status(client)
            publish_sensors(client)
        time.sleep(DEVICE_LOOP_INTERVAL)


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


def _post_face_image(url, image_bytes):
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    payload = {
        "home_id": HOME_ID,
        "device_id": DEVICE_ID,
        "image_base64": image_b64,
    }
    response = requests.post(url, json=payload, timeout=10.0)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return None


def face_send_loop():
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
                    # Chỉ mở cửa qua MQTT (backend publish đúng home_id/device_id); không mở cửa cục bộ.
                    log("face_verify: match -> expect door command on {}".format(COMMAND_TOPIC))
                    last_verify_ts = now
            else:
                log("face_upload: sending to server")
                _post_face_image(FACE_UPLOAD_URL, image_bytes)
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
        threading.Thread(target=device_loop, args=(client,), daemon=True),
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
