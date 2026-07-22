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


def _create_database_if_not_exists() -> None:
    """Connect to default 'postgres' database and create target database if missing."""
    if settings.DATABASE_URL.startswith("sqlite"):
        return
    try:
        from sqlalchemy.engine.url import make_url
        from sqlalchemy import create_engine, text
        
        url = make_url(settings.DATABASE_URL)
        db_name = url.database
        if not db_name:
            return
            
        default_url = url.set(database="postgres")
        # Use AUTOCOMMIT to execute CREATE DATABASE outside a transaction
        temp_engine = create_engine(default_url, isolation_level="AUTOCOMMIT")
        
        with temp_engine.connect() as conn:
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"))
            if not result.scalar():
                import logging
                logging.getLogger("dekho").info(f"🐘 Database '{db_name}' does not exist. Creating it locally...")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
        temp_engine.dispose()
    except Exception as e:
        import logging
        logging.getLogger("dekho").warning(f"Could not verify/create database: {e}")


def init_db() -> None:
    """
    Create all tables defined in ORM models.
    Safe to call multiple times (CREATE TABLE IF NOT EXISTS).
    Called once at server startup from run.py.
    Also pings the DB to wake up Neon serverless compute before first request.
    """
    # 1. Create database if it does not exist locally
    _create_database_if_not_exists()

    # 2. Import all models so SQLAlchemy knows about them before creating tables
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # 3. Import data from local JSON backup if SQLite is empty
    db = SessionLocal()
    try:
        import_from_json_file(db)
    finally:
        db.close()

    # 4. Warmup ping: wake up database and verify connection
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
    except Exception as warmup_err:
        # Non-fatal -- log and continue, requests may still be slow on first hit
        import logging
        logging.getLogger("dekho").warning(f"DB warmup ping failed: {warmup_err}")

# ---------------------------------------------------------------------------
# JSON Storage Sync Layer
# ---------------------------------------------------------------------------
import json
import os
from sqlalchemy.orm import Session
from sqlalchemy import event

# Resolved relative to settings.DATA_DIR (which points to root/data)
JSON_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "local_db.json"))

def get_all_models():
    import app.models as models
    return [
        models.User,
        models.Transaction,
        models.SavingsGoal,
        models.Budget,
        models.Asset,
        models.Recommendation,
        models.MerchantMapping,
        models.FeedbackLog,
        models.UploadedFile,
        models.RawRecord,
    ]

def export_to_json_file(db: Session = None):
    try:
        from app.core.database import SessionLocal
        export_db = SessionLocal()
        try:
            data = {}
            for model in get_all_models():
                table_name = model.__tablename__
                rows = export_db.query(model).all()
                row_dicts = []
                for row in rows:
                    row_dict = {}
                    for col in row.__table__.columns:
                        val = getattr(row, col.name)
                        if val is not None and hasattr(val, "isoformat"):
                            val = val.isoformat()
                        elif val is not None and hasattr(val, "strftime"):
                            val = str(val)
                        row_dict[col.name] = val
                    row_dicts.append(row_dict)
                data[table_name] = row_dicts
            
            os.makedirs(os.path.dirname(JSON_DB_PATH), exist_ok=True)
            with open(JSON_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        finally:
            export_db.close()
    except Exception as e:
        import logging
        logging.getLogger("dekho").error(f"Error exporting database to JSON: {e}")

def import_from_json_file(db: Session):
    if not os.path.exists(JSON_DB_PATH):
        return
    try:
        import logging
        logger = logging.getLogger("dekho")
        logger.info(f"Loading data from local JSON backup: {JSON_DB_PATH}")
        with open(JSON_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        any_restored = False
        for model in get_all_models():
            table_name = model.__tablename__
            if table_name not in data or not data[table_name]:
                continue
            
            # Only populate if the table is currently empty
            if db.query(model).count() > 0:
                continue
                
            logger.info(f"Restoring table '{table_name}' from JSON...")
            any_restored = True
            for row_dict in data[table_name]:
                from sqlalchemy import DateTime, Date
                processed_dict = {}
                for col in model.__table__.columns:
                    val = row_dict.get(col.name)
                    if val is not None:
                        if isinstance(col.type, (DateTime, Date)) and isinstance(val, str):
                            try:
                                if "T" in val:
                                    from datetime import datetime
                                    processed_dict[col.name] = datetime.fromisoformat(val)
                                else:
                                    from datetime import date
                                    processed_dict[col.name] = date.fromisoformat(val)
                            except Exception:
                                processed_dict[col.name] = val
                        else:
                            processed_dict[col.name] = val
                            
                instance = model(**processed_dict)
                db.add(instance)
        if any_restored:
            db.commit()
            logger.info("✅ JSON restore completed successfully!")
    except Exception as e:
        import logging
        logging.getLogger("dekho").error(f"Error importing database from JSON: {e}")

# Register automatic event listener to dump SQLite to JSON file after every commit
@event.listens_for(Session, 'after_commit')
def receive_after_commit(session):
    if settings.DATABASE_URL.startswith("sqlite"):
        export_to_json_file(session)
