# app/api/routes/health_controller.py
# ─────────────────────────────────────────────────────────────────
# Health check controller for monitoring and load balancers.
# Returns service status, uptime, and database connectivity.
# ─────────────────────────────────────────────────────────────────

from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.database.connection import get_pool

router = APIRouter(tags=["Health"])

# Record service start time for uptime calculation
_start_time = datetime.now(timezone.utc)


@router.get("/health", summary="Service Health Check")
async def health_check() -> dict:
    """
    Performs a health check of the service and its dependencies.
    Checks connectivity to the collection database.
    """
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()
    
    db_healthy = True
    db_error = None
    
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            # Simple query to verify database connectivity
            await conn.fetchval("SELECT 1")
    except Exception as e:
        db_healthy = False
        db_error = str(e)
        
    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": settings.service_name,
        "environment": settings.app_env,
        "uptime_seconds": round(uptime, 2),
        "database_connected": db_healthy,
        "database_error": db_error,
        "model": settings.openai_model,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
