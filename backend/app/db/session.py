"""
Database Session — Sync & Async Engines with Connection Pooling
TOP WorX ERP System

Provides:
- Sync engine + session (for Alembic migrations, scripts)
- Async engine + session (for FastAPI endpoints)
- Configurable connection pooling (pool size, overflow, timeouts)
- Health check / pool status monitoring
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# SYNC ENGINE (for Alembic, scripts, finance sync endpoints)
# ═════════════════════════════════════════════════════════════════════════════

sync_engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,       # Recycle connections every 30 min
    pool_reset_on_return="commit",
    echo=settings.DEBUG,     # Log SQL in debug mode
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


def get_sync_db():
    """Get a synchronous database session (for Alembic, scripts)."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ═════════════════════════════════════════════════════════════════════════════
# ASYNC ENGINE (for FastAPI endpoints)
# ═════════════════════════════════════════════════════════════════════════════

# Pool configuration — tunable via environment variables
ASYNC_POOL_SIZE = settings.ASYNC_POOL_SIZE if hasattr(settings, 'ASYNC_POOL_SIZE') else 20
ASYNC_MAX_OVERFLOW = settings.ASYNC_MAX_OVERFLOW if hasattr(settings, 'ASYNC_MAX_OVERFLOW') else 30
ASYNC_POOL_TIMEOUT = settings.ASYNC_POOL_TIMEOUT if hasattr(settings, 'ASYNC_POOL_TIMEOUT') else 30
ASYNC_POOL_RECYCLE = settings.ASYNC_POOL_RECYCLE if hasattr(settings, 'ASYNC_POOL_RECYCLE') else 1800

async_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=ASYNC_POOL_SIZE,
    max_overflow=ASYNC_MAX_OVERFLOW,
    pool_timeout=ASYNC_POOL_TIMEOUT,
    pool_recycle=ASYNC_POOL_RECYCLE,
    pool_reset_on_return="commit",
    echo=settings.DEBUG,     # Log SQL in debug mode
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ═════════════════════════════════════════════════════════════════════════════
# DEPENDENCY — FastAPI injects this per request
# ═════════════════════════════════════════════════════════════════════════════

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async DB session.
    Commits on success, rolls back on exception, always closes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ═════════════════════════════════════════════════════════════════════════════
# POOL MONITORING — for health checks and production monitoring
# ═════════════════════════════════════════════════════════════════════════════

def get_pool_status() -> dict:
    """Return async pool statistics for monitoring dashboards."""
    pool = async_engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_connections": pool.checkedin() + pool.checkedout(),
        "max_overflow": ASYNC_MAX_OVERFLOW,
        "pool_timeout": ASYNC_POOL_TIMEOUT,
        "pool_recycle": ASYNC_POOL_RECYCLE,
    }


async def check_db_health() -> dict:
    """
    Verify database connectivity and pool health.
    Returns status dict for /health endpoint.
    """
    status = {
        "database": "unknown",
        "pool": get_pool_status(),
    }
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
            status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"unhealthy: {str(e)}"
        logger.error(f"Database health check failed: {e}")
    return status


# ═════════════════════════════════════════════════════════════════════════════
# ENGINE DISPOSAL — call on app shutdown
# ═════════════════════════════════════════════════════════════════════════════

async def dispose_engines():
    """Dispose both engines cleanly on application shutdown."""
    await async_engine.dispose()
    sync_engine.dispose()
    logger.info("Database engines disposed")
