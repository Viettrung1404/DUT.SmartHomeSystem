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

# MQTT
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "test.mosquitto.org")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_COMMAND_TOPIC = os.getenv("MQTT_COMMAND_TOPIC", "smarthome/commands")
DOOR_OPEN_COMMAND = os.getenv("DOOR_OPEN_COMMAND", "door open")

# WebSocket
WS_PING_INTERVAL = int(os.getenv("WS_PING_INTERVAL", 30))

# Backend URL (for mobile app)
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

# Email / password reset
SMTP_HOST = os.getenv("SMTP_HOST") or os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "true").lower() == "true"
PASSWORD_RESET_BASE_URL = os.getenv("PASSWORD_RESET_BASE_URL", f"http://{BACKEND_HOST}:{BACKEND_PORT}")
