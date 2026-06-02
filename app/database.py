from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# ─── Engine ──────────────────────────────────────────────────────────────────
# connect_args is only needed for SQLite (disables same-thread check for async)
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.APP_DEBUG,  # logs SQL in debug mode
    pool_pre_ping=True,
)

# Enable foreign key enforcement for SQLite (disabled by default)
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# ─── Session factory ─────────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── Base class for all ORM models ───────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Dependency for FastAPI routes ───────────────────────────────────────────
def get_db():
    """Yield a database session and ensure it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
