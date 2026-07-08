import asyncpg
from app.config import settings

_pool = None

async def init_pool():
    global _pool
    # Replace postgresql+asyncpg:// with postgresql:// if needed for asyncpg
    db_url = settings.database_url
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    
    _pool = await asyncpg.create_pool(
        db_url,
        min_size=2,
        max_size=10,
        max_queries=1000,
        max_inactive_connection_lifetime=300
    )

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database connection pool has not been initialized.")
    return _pool
