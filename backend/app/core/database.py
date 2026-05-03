from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# -----------------------------------------------------------------------
# Engine — with connection pool tuning for Neon (serverless Postgres)
# Neon connections can be slow to cold-start; timeouts prevent hangs.
# -----------------------------------------------------------------------
_is_postgres = not settings.DATABASE_URL.startswith("sqlite")

_engine_kwargs: dict = {}

if _is_postgres:
    _engine_kwargs = {
        # Pool size: keep 5 live connections; allow 10 overflow under load
        "pool_size": 5,
        "max_overflow": 10,
        # Recycle connections every 10 min to avoid Neon's idle disconnects
        "pool_recycle": 600,
        # Wait at most 10 s for a free connection before giving up
        "pool_timeout": 10,
        # Validate connections before using them (avoids "connection closed" errors)
        "pool_pre_ping": True,
        # Connect timeout: allow up to 30s for Neon cold-start wake-up
        "connect_args": {
            "connect_timeout": 30,
        },
    }
else:
    _engine_kwargs = {
        "connect_args": {"check_same_thread": False},
    }

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency -- yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables defined in ORM models.
    Safe to call multiple times (CREATE TABLE IF NOT EXISTS).
    Called once at server startup from run.py.
    Also pings the DB to wake up Neon serverless compute before first request.
    """
    # Import all models so SQLAlchemy knows about them before creating tables
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Warmup ping: wake up Neon if it was paused (can take 5-15s on free tier)
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
    except Exception as warmup_err:
        # Non-fatal -- log and continue, requests may still be slow on first hit
        import logging
        logging.getLogger("dekho").warning(f"DB warmup ping failed: {warmup_err}")
