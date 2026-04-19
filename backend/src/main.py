from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.core import engine, Base, SessionLocal
from .api import register_routes
from .logging import configure_logging, LogLevels
from .mqtt_client import get_mqtt_client

from .websocket import ws_manager
from .mqtt_client import get_mqtt_client, init_mqtt
from .automation.engine import init_automation_engine, stop_automation_engine
import logging

# Import all entities so they are registered with Base.metadata
from .entities.user import User
from .entities.home import Home
from .entities.home_member import HomeMember
from .entities.room import Room
from .entities.device import Device
from .entities.device_log import DeviceLog
from .entities.automation import Automation, AutomationCondition, AutomationAction
from .entities.energy_log import EnergyLog
from .entities.security_event import SecurityEvent

configure_logging(LogLevels.info)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logging.info("Starting Smart Home backend...")
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created")
    except Exception as e:
        # Avoid blocking API startup in mixed-schema dev environments.
        logging.warning(f"Skipping create_all due to schema mismatch: {e}")

    # Initialize MQTT with DB session factory and WS manager
    init_mqtt(SessionLocal, ws_manager)
    try:
        get_mqtt_client()
        logging.info("MQTT client initialized")
    except Exception as e:
        logging.warning(f"MQTT client failed to start: {e}")

    # Initialize automation engine
    try:
        init_automation_engine(SessionLocal)
        logging.info("Automation engine initialized")
    except Exception as e:
        logging.warning(f"Automation engine failed to start: {e}")

    yield

    # Shutdown
    try:
        stop_automation_engine()
    except Exception:
        pass
    logging.info("Smart Home backend stopped")


app = FastAPI(
    title="Smart Home API",
    description="Backend API for Smart Home System — FastAPI + PostgreSQL + MQTT + WebSocket",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routes(app)


@app.on_event("startup")
async def startup_mqtt() -> None:
	get_mqtt_client()