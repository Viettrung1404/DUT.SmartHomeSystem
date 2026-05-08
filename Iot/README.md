# Iot

Simple MQTT device client for Raspberry Pi.

## Setup

1) Create venv and install deps:

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

2) Set env vars (example for public broker):

set MQTT_BROKER_HOST=test.mosquitto.org
set MQTT_BROKER_PORT=1883
set HOME_ID=home-001
set DEVICE_ID=<uuid-tu-bang-devices-tren-backend>
set RAIN_PIN=21
set RAIN_ACTIVE_LOW=1
set RAIN_SERVO_ENABLED=1
set RAIN_SERVO_PIN=26
set RAIN_SERVO_DRY_ANGLE=0
set RAIN_SERVO_WET_ANGLE=190

3) Run:

python device_client.py

## All-in-one IoT client

This runs device sensors, MQTT commands, and face upload in one process.

python3 Iot/iot_client.py

### Raspberry Camera notes (legacy vs libcamera)

- If you are on newer Raspberry Pi OS (libcamera stack), install picamera2:

sudo apt update
sudo apt install -y python3-picamera2

- Select camera backend with env var (default: auto):

export CAMERA_BACKEND=auto

Valid values: auto, picamera2, picamera, opencv.

## Face detection client

This client detects a face on the Raspberry Pi and sends it to the backend for recognition.

1) Set env vars:

set FACE_SERVER_URL=http://localhost:8000/face/verify
set FACE_ENROLL_URL=http://localhost:8000/face/enroll
set FACE_MODE=verify
set HOME_ID=home-001

2) Run:

python face_client.py

To enroll a person, set:

set FACE_MODE=enroll
set PERSON_ID=alice
python face_client.py

## Notes

- Default broker is test.mosquitto.org if env vars are not set.
- Phase A MQTT contract: the preferred topics are `device/{DEVICE_ID}/status` and `device/{DEVICE_ID}/command`.
- If MQTT connect fails with DNS errors on Raspberry Pi, set `MQTT_BROKER_HOST` to a resolvable hostname or IP and verify the device has working network/DNS.
- Commands supported: on, off, toggle, status
- Rain sensor is read from `RAIN_PIN` and published as `rain_detected` in status/sensor payloads.
- Optional rain servo: when `rain_detected=true`, servo on `RAIN_SERVO_PIN` rotates to `RAIN_SERVO_WET_ANGLE` (default 190); when dry, it returns to `RAIN_SERVO_DRY_ANGLE` (default 0).

## Rain Servo Test

Use this standalone script on the Raspberry Pi to test the rain servo without running the full IoT client.

python3 test_rain_servo.py --wet
python3 test_rain_servo.py --dry

If you run it without arguments, it defaults to `--dry`.

Default pins:
- Servo signal: GPIO 26
