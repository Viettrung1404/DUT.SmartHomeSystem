import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# JWT Authentication
SECRET_KEY = os.getenv("SECRET_KEY", '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3')
ALGORITHM = os.getenv("ALGORITHM", 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Face recognition
FACE_GALLERY_DIR = os.getenv("FACE_GALLERY_DIR", "data/face_gallery")
FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "0.55"))
FACE_MODEL_NAME = os.getenv("FACE_MODEL_NAME", "buffalo_l")
FACE_PROVIDER = os.getenv("FACE_PROVIDER", "CPUExecutionProvider")
FACE_DET_SIZE = os.getenv("FACE_DET_SIZE", "640,640")
FACE_LAST_IMAGE_PATH = os.getenv("FACE_LAST_IMAGE_PATH", "data/face_last.jpg")

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "0d847a93f8b9463487a312fdd241108a.s1.eu.hivemq.cloud")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "8883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "testuser")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "19122005Tri")

# Topic layout: {prefix}/{home_id}/{device_id}/{commands|status|sensors}
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "smarthome").strip().strip("/")

# When API clients omit home_id / device_id, use these (HOME_ID/DEVICE_ID still work in .env)
DEFAULT_HOME_ID = os.getenv("HOME_ID") or os.getenv("DEFAULT_HOME_ID") or "home-001"
DEFAULT_DEVICE_ID = os.getenv("DEVICE_ID") or os.getenv("DEFAULT_DEVICE_ID") or "raspi-01"

DOOR_OPEN_COMMAND = os.getenv("DOOR_OPEN_COMMAND", "door open")

# WebSocket
WS_PING_INTERVAL = int(os.getenv("WS_PING_INTERVAL", 30))

# Backend URL (for mobile app)
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
