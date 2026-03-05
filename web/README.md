# web

Minimal web controller that publishes MQTT commands and shows last device status.

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
set WEB_PORT=8000

3) Run:

python app.py

Open http://localhost:8000

## Notes

- Default broker is test.mosquitto.org if env vars are not set.
- This app uses a background MQTT client to publish commands and read status.
