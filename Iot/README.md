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
set MQTT_COMMAND_TOPIC=smarthome/commands
set MQTT_STATUS_TOPIC=smarthome/status
set DEVICE_ID=raspi-01

3) Run:

python device_client.py

## All-in-one IoT client

This runs device sensors, MQTT commands, and face upload in one process.

python3 Iot/iot_client.py

## Face detection client

This client detects a face on the Raspberry Pi and sends it to the backend for recognition.

1) Set env vars:

set FACE_SERVER_URL=http://localhost:8000/face/verify
set FACE_ENROLL_URL=http://localhost:8000/face/enroll
set FACE_MODE=verify
set DEVICE_ID=raspi-01

2) Run:

python face_client.py

To enroll a person, set:

set FACE_MODE=enroll
set PERSON_ID=alice
python face_client.py

## Notes

- Default broker is test.mosquitto.org if env vars are not set.
- Commands supported: on, off, toggle, status
