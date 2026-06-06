from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat_routes import router as chat_router
from app.api.health_routes import router as health_router
from app.logging_config import configure_logging


configure_logging()


app = FastAPI(
    title="Smart Home AI Server",
    description="Tool-augmented RAG assistant for the Smart Home backend.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)
