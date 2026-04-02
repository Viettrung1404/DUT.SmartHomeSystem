from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from .database.core import engine, Base, SessionLocal
from .api import register_routes
from .logging import configure_logging, LogLevels
from .websocket import ws_manager
from .mqtt_client import get_mqtt_client, init_mqtt, set_event_loop
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
from .entities.suggestion_log import SuggestionLog
from .entities.auth_session import AuthSession
from .entities.password_reset_token import PasswordResetToken

configure_logging(LogLevels.info)


def _ensure_legacy_schema_compatibility() -> None:
    """Patch known DB schema drift for existing local Postgres volumes."""
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    missing_columns = {"role", "is_active"} - user_columns
    if not missing_columns:
        return

    logging.warning(
        "Schema drift detected on users table. Missing columns: %s. Applying compatibility patch...",
        ", ".join(sorted(missing_columns)),
    )
    with engine.begin() as conn:
        if "role" in missing_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20)"))
            conn.execute(text("UPDATE users SET role = 'MEMBER' WHERE role IS NULL"))
            conn.execute(text("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'MEMBER'"))
            conn.execute(text("ALTER TABLE users ALTER COLUMN role SET NOT NULL"))

        if "is_active" in missing_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN"))
            conn.execute(text("UPDATE users SET is_active = TRUE WHERE is_active IS NULL"))
            conn.execute(text("ALTER TABLE users ALTER COLUMN is_active SET DEFAULT TRUE"))
            conn.execute(text("ALTER TABLE users ALTER COLUMN is_active SET NOT NULL"))

    logging.info("Compatibility patch applied for users table")


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
    set_event_loop(asyncio.get_running_loop())
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