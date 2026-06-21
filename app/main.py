# app/main.py
# ─────────────────────────────────────────────────────────────────
# FastAPI application entry point.
# Manages the service lifecycle (startup/shutdown), middleware,
# and route registration for the ClimaSync Risk Analysis Agent.
# ─────────────────────────────────────────────────────────────────

# Load .env into os.environ FIRST — the OpenAI Agents SDK reads
# OPENAI_API_KEY from os.environ, not from pydantic-settings.
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import setup_logger
from app.database.connection import create_pool, close_pool
from app.api.routes.assessment_controller import router as assess_router
from app.api.routes.health_controller import router as health_router

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application lifecycle.
    Ensures database resources are initialized on startup and 
    cleaned up on shutdown.
    """
    # ── STARTUP ───────────────────────────────────────────────────
    logger.info(
        f"Starting {settings.service_name} on port {settings.app_port}..."
    )

    # Initialize the database connection pool
    try:
        await create_pool()
        logger.info("Collection database connection pool initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        # We allow startup to continue so /health can report the failure
    
    logger.info(
        f"{settings.service_name} ready. "
        f"Environment: {settings.app_env} | "
        f"Model: {settings.openai_model}"
    )

    yield  # Application runs here

    # ── SHUTDOWN ──────────────────────────────────────────────────
    logger.info(f"Shutting down {settings.service_name}...")
    
    await close_pool()
    
    logger.info("Shutdown sequence complete.")


# Create the FastAPI application instance
app = FastAPI(
    title="ClimaSync Risk Analysis Agent",
    description=(
        "AI-powered disaster risk assessment service for Pakistan. "
        "Analyzes flood, earthquake, and extreme weather events "
        "using multi-source data and agentic reasoning."
    ),
    version="2.0.0",
    lifespan=lifespan,
    # Disable docs in production for security
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url=None,
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health_router)
app.include_router(assess_router)


if __name__ == "__main__":
    import uvicorn
    
    # Run the application using Uvicorn
    # timeout_keep_alive=300 prevents the connection from being
    # closed during long-running agent assessments (2-4 minutes).
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.app_env == "development",
        timeout_keep_alive=300,
    )
