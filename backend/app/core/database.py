from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    # SQLite needs this flag; ignored by Postgres
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
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
    """
    # Import all models so SQLAlchemy knows about them before creating tables
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
