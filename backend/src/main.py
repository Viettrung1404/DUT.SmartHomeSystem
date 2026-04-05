from fastapi import FastAPI
from .database.core import engine, Base
from .entities.todo import Todo
from .entities.user import User
from .api import register_routes
from .logging import configure_logging, LogLevels
from .mqtt_client import get_mqtt_client


configure_logging(LogLevels.info)

app = FastAPI()

Base.metadata.create_all(bind=engine)

register_routes(app)


@app.on_event("startup")
async def startup_mqtt() -> None:
	get_mqtt_client()