# app/database/connection.py
# ─────────────────────────────────────────────────────────────────
# Async PostgreSQL connection pool using asyncpg.
# Connects to the DATA COLLECTION DATABASE in READ-ONLY mode.
# Pool is created at startup and closed at shutdown.
# ─────────────────────────────────────────────────────────────────

import asyncpg
from asyncpg import Pool
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Module-level pool — shared across all requests
_pool: Pool | None = None


async def _init_connection(conn) -> None:
    """
    Runs on every new connection from the pool.
    Sets timezone to Asia/Karachi for correct date calculations.
    """
    await conn.execute("SET timezone = 'Asia/Karachi'")


async def create_pool() -> None:
    """
    Creates the asyncpg connection pool.
    Called once during FastAPI startup.
    Sets timezone to Asia/Karachi on every connection.
    """
    global _pool

    logger.info("Connecting to collection database...")

    _pool = await asyncpg.create_pool(
        host=settings.collection_db_host,
        port=settings.collection_db_port,
        database=settings.collection_db_name,
        user=settings.collection_db_user,
        password=settings.collection_db_password,
        min_size=settings.collection_db_pool_min,
        max_size=settings.collection_db_pool_max,
        init=_init_connection,
        command_timeout=30,
    )

    # Test the connection
    async with _pool.acquire() as conn:
        result = await conn.fetchval("SELECT 1")
        if result != 1:
            raise ConnectionError("Database health check failed")

    logger.info(
        f"Collection database connected. "
        f"Pool size: {settings.collection_db_pool_min}-{settings.collection_db_pool_max}"
    )


async def close_pool() -> None:
    """
    Closes the connection pool.
    Called during FastAPI shutdown.
    """
    global _pool
    if _pool:
        await _pool.close()
        logger.info("Collection database pool closed")


def get_pool() -> Pool:
    """
    Returns the active connection pool.
    Raises RuntimeError if pool not initialized.
    Used as FastAPI dependency.
    """
    if _pool is None:
        raise RuntimeError(
            "Database pool not initialized. "
            "Call create_pool() during startup."
        )
    return _pool
