# app/core/config.py
# ─────────────────────────────────────────────────────────────────
# Central configuration management using pydantic-settings.
# All environment variables are validated at startup.
# If any required variable is missing, the service refuses to start.
# ─────────────────────────────────────────────────────────────────

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # ── OpenAI ────────────────────────────────────────────────────
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(
        default="gpt-4o",
        description="Model for risk analysis agent"
    )
    openai_max_turns: int = Field(
        default=25,
        description="Maximum agent reasoning turns"
    )

    # ── Collection Database ───────────────────────────────────────
    collection_db_host: str = Field(
        ..., description="Collection DB hostname"
    )
    collection_db_port: int = Field(
        default=5432, description="Collection DB port"
    )
    collection_db_name: str = Field(
        default="postgres", description="Collection DB name"
    )
    collection_db_user: str = Field(
        default="postgres", description="Collection DB user"
    )
    collection_db_password: str = Field(
        ..., description="Collection DB password"
    )
    collection_db_pool_min: int = Field(
        default=2, description="Minimum DB pool connections"
    )
    collection_db_pool_max: int = Field(
        default=8, description="Maximum DB pool connections"
    )

    # ── Service ───────────────────────────────────────────────────
    app_port: int = Field(default=8001)
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    service_name: str = Field(
        default="climasync-risk-analysis-agent"
    )

    # ── Security ──────────────────────────────────────────────────
    internal_api_key: str = Field(
        ..., description="API key for main system auth"
    )

    # ── Main System ───────────────────────────────────────────────
    main_system_base_url: str = Field(
        default="http://localhost:8001"
    )
    main_system_api_key: str = Field(
        ..., description="Key to call main system"
    )

    # ── Pakistan Bounds ───────────────────────────────────────────
    pakistan_min_lat: float = Field(default=23.0)
    pakistan_max_lat: float = Field(default=38.0)
    pakistan_min_lon: float = Field(default=60.0)
    pakistan_max_lon: float = Field(default=78.0)

    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=False,
        extra="ignore"
    )


# Singleton instance — import this everywhere
settings = Settings()
