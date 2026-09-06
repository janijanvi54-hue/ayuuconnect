"""Health check endpoint used to verify the service and DB connectivity."""

from flask import Blueprint, current_app
from sqlalchemy import text

from ..extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health():
    db_ok = False
    try:
        db.session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db.session.rollback()

    payload = {
        "service": "ayuconnect-api",
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unavailable",
        "environment": current_app.config.get("FLASK_ENV", "development"),
        "ai_provider": current_app.config.get("AI_PROVIDER", "demo"),
    }
    status = 200 if db_ok else 503
    return (
        {
            "success": db_ok,
            "message": "AYUConnect API is running",
            "data": payload,
        },
        status,
    )