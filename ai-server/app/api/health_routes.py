from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import SessionLocal
from app.llm.ollama_client import check_ollama

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    db_status = "ok"
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "ollama": check_ollama(),
        "db": db_status,
    }

