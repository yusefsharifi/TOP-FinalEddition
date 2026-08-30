from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import uvicorn
from typing import Dict, Any
from datetime import datetime
import logging

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.cache import cache, warm_cache
from app.db.session import check_db_health, get_pool_status, dispose_engines

logger = logging.getLogger(__name__)


# ── Application lifespan (startup / shutdown) ──────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle — startup and shutdown events."""
    # STARTUP
    logger.info(f"Starting TOP WorX ERP ({settings.ENVIRONMENT})")
    logger.info(f"Async pool: size={settings.ASYNC_POOL_SIZE}, "
                f"max_overflow={settings.ASYNC_MAX_OVERFLOW}, "
                f"timeout={settings.ASYNC_POOL_TIMEOUT}s")

    # Connect to Redis cache
    try:
        await cache.connect(settings.REDIS_URL)
    except Exception as e:
        logger.warning(f"Redis cache unavailable: {e}")

    # Start AI Workflow Scheduler
    try:
        from app.core.ai.workflow_scheduler import get_scheduler
        from app.db.session import AsyncSessionLocal

        async def scheduler_db_factory():
            session = AsyncSessionLocal()
            try:
                yield session
            finally:
                await session.close()

        scheduler = get_scheduler(db_factory=scheduler_db_factory)
        # Add default jobs (but don't auto-start — must be started via API)
        from app.core.ai.workflow_handlers import WORKFLOW_HANDLERS
        default_intervals = {
            "low_stock_auto_po": 60,
            "invoice_due_reminder": 360,
            "lead_high_score_assign": 1440,
            "expense_anomaly_alert": 1440,
            "employee_anniversary_review": 1440,
            "project_delay_escalation": 240,
            "quality_issue_quarantine": 240,
            "customer_churn_retention": 1440,
        }
        for name, interval in default_intervals.items():
            if name in WORKFLOW_HANDLERS:
                scheduler.add_job(name, interval_minutes=interval)
        logger.info(f"AI Scheduler initialized with {len(default_intervals)} jobs")
    except Exception as e:
        logger.warning(f"AI Scheduler init failed: {e}")

    yield

    # SHUTDOWN
    # Stop AI Scheduler
    try:
        from app.core.ai.workflow_scheduler import get_scheduler
        scheduler = get_scheduler()
        scheduler.stop()
    except Exception:
        pass

    await cache.disconnect()
    await dispose_engines()
    logger.info("TOP WorX ERP shutdown complete")


app = FastAPI(
    title="TOP WorX ERP System",
    description="Comprehensive ERP system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Health check endpoint
@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    db_health = await check_db_health()
    cache_stats = await cache.get_stats()
    return {
        "status": "healthy" if db_health["database"] == "healthy" else "degraded",
        "version": "1.0.0",
        "company": "TOP WorX",
        "database": db_health,
        "cache": cache_stats,
        "environment": settings.ENVIRONMENT,
    }

# Pool monitoring endpoint (admin only in production)
@app.get("/api/pool-status")
async def pool_status() -> Dict[str, Any]:
    return get_pool_status()

# Cache stats endpoint
@app.get("/api/cache-stats")
async def cache_stats() -> Dict[str, Any]:
    return await cache.get_stats()

# Cache clear endpoint (admin only in production)
@app.post("/api/cache-clear")
async def cache_clear() -> Dict[str, Any]:
    await cache.clear()
    return {"status": "cleared"}

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 