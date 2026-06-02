"""
Health check endpoint.

GET /health  →  returns server status + database connectivity check.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Server and database health check")
def health_check(db: Session = Depends(get_db)):
    """
    Returns the operational status of the server and its database connection.

    - **status**: `ok` if everything is healthy, `degraded` if DB is unreachable.
    - **database**: `connected` or an error message.
    - **timestamp**: current UTC time on the server.
    """
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        db_status = f"error: {exc}"

    overall = "ok" if db_status == "connected" else "degraded"

    return {
        "status": overall,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
