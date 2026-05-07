# ClimaSync.ai — Risk Analysis Agent
## Complete Production Development Document

---

## DOCUMENT PURPOSE

This document is the complete, unambiguous, production-ready development specification for the ClimaSync.ai Risk Analysis Agent. Every file, every function, every configuration, every database query, every scoring rule, and every design decision is documented here with full explanation. A developer or AI reading this document has everything needed to build this agent completely without asking any additional questions.

---

## PART 1: COMPLETE SYSTEM CONTEXT

### 1.1 Where This Agent Lives

```
┌──────────────────────────────────────────────────────────────────┐
│                    CLIMASYNC COMPLETE PIPELINE                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DATA COLLECTION SERVICE (Port 8000)                             │
│  └── Detects breach → writes to threshold_breach_log             │
│  └── Dispatches to Main System                                   │
│           ↓                                                      │
│  MAIN CLIMASYNC BACKEND (Port 8001)                              │
│  └── Admin Portal receives breach alert                          │
│  └── Admin reviews and clicks "Trigger Risk Analysis"            │
│  └── Main backend calls Risk Analysis Agent                      │
│           ↓                                                      │
│  ┌─────────────────────────────────────────────────┐             │
│  │   RISK ANALYSIS AGENT (Port 8002)  ← BUILD THIS │             │
│  │   FastAPI + OpenAI Agents SDK                   │             │
│  │   Reads: Collection DB (read-only)              │             │
│  │   Uses: Web Search Tool                         │             │
│  │   Produces: RiskAssessmentReport JSON           │             │
│  └─────────────────────────────────────────────────┘             │
│           ↓                                                      │
│  PRECAUTION DEFINER AGENT (Port 8003)                            │
│  └── Receives RiskAssessmentReport                               │
│  └── Generates actionable safety plans                           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 What This Agent Receives

```
Input from Main System (POST /api/v1/assess):
{
  "breach_id": "uuid-string",
  "disaster_kind": "flood",
  "location_name": "Sukkur",
  "district": "sukkur",
  "province": "sindh",
  "latitude": 27.7052,
  "longitude": 68.8574,
  "observed_value": 105.3,
  "threshold_value": 100.0,
  "breach_severity": "emergency",
  "metric_name": "gauge_pct_of_danger",
  "observation_time": "2025-07-15T14:30:00+05:00",
  "is_forecast_breach": false,
  "forecast_horizon_h": null,
  "source_api": "google_flood_hub",
  "gauge_id": "uuid-string",
  "usgs_event_id": null,
  "weather_location_id": "uuid-string"
}
```

### 1.3 What This Agent Produces

```
Output RiskAssessmentReport JSON stored in:
  Main ClimaSync Database → risk_assessments table
  Returned in HTTP response to main system
  Passed to Precaution Definer Agent
```

---

## PART 2: PROJECT SETUP

### 2.1 Complete Directory Structure

```
risk_analysis_agent/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── exceptions.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── queries/
│   │       ├── __init__.py
│   │       ├── location_queries.py
│   │       ├── infrastructure_queries.py
│   │       └── disaster_data_queries.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── input_models.py
│   │   └── output_models.py
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── risk_agent.py
│   │   ├── system_prompt.py
│   │   │
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── location_tool.py
│   │   │   ├── infrastructure_tool.py
│   │   │   ├── disaster_data_tool.py
│   │   │   └── web_search_tool.py
│   │   │
│   │   └── scoring/
│   │       ├── __init__.py
│   │       ├── terrain_classifier.py
│   │       ├── hazard_scorer.py
│   │       ├── exposure_scorer.py
│   │       ├── vulnerability_scorer.py
│   │       ├── escalation_scorer.py
│   │       ├── response_scorer.py
│   │       └── composite_scorer.py
│   │
│   └── api/
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           ├── assessment_controller.py
│           └── health_controller.py
│
├── tests/
│   ├── __init__.py
│   ├── test_scoring.py
│   ├── test_tools.py
│   └── test_agent.py
│
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

### 2.2 pyproject.toml

```toml
[project]
name = "climasync-risk-analysis-agent"
version = "1.0.0"
description = "ClimaSync Risk Analysis Agent"
requires-python = ">=3.12"

dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "openai-agents",
    "openai",
    "asyncpg",
    "pydantic",
    "pydantic-settings",
    "httpx",
    "python-dotenv",
    "tenacity",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 2.3 .env.example

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TURNS=25

# Collection Database (READ ONLY)
COLLECTION_DB_HOST=your-supabase-host.supabase.co
COLLECTION_DB_PORT=5432
COLLECTION_DB_NAME=postgres
COLLECTION_DB_USER=postgres
COLLECTION_DB_PASSWORD=your-collection-db-password
COLLECTION_DB_POOL_MIN=2
COLLECTION_DB_POOL_MAX=8

# Service Configuration
APP_PORT=8002
APP_ENV=production
LOG_LEVEL=INFO
SERVICE_NAME=climasync-risk-analysis-agent

# Internal Security
INTERNAL_API_KEY=your-internal-api-key-here

# Main System Callback
MAIN_SYSTEM_BASE_URL=http://localhost:8001
MAIN_SYSTEM_API_KEY=your-main-system-api-key

# Pakistan Geographic Bounds
PAKISTAN_MIN_LAT=23.0
PAKISTAN_MAX_LAT=38.0
PAKISTAN_MIN_LON=60.0
PAKISTAN_MAX_LON=78.0
```

---

## PART 3: CORE INFRASTRUCTURE FILES

### 3.1 app/core/config.py

```python
# app/core/config.py
# ─────────────────────────────────────────────────────────────────
# Central configuration management using pydantic-settings.
# All environment variables are validated at startup.
# If any required variable is missing, the service refuses to start.
# ─────────────────────────────────────────────────────────────────

from pydantic_settings import BaseSettings
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
    app_port: int = Field(default=8002)
    app_env: str = Field(default="production")
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

    model_config = {"env_file": ".env", "case_sensitive": False}


# Singleton instance — import this everywhere
settings = Settings()
```

### 3.2 app/core/logger.py

```python
# app/core/logger.py
# ─────────────────────────────────────────────────────────────────
# Centralized structured logging.
# All logs include timestamp in PKT, service name, and log level.
# ─────────────────────────────────────────────────────────────────

import logging
import sys
from app.core.config import settings


def setup_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger instance.
    Usage: logger = setup_logger(__name__)
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.log_level.upper()))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.log_level.upper()))

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
```

### 3.3 app/core/exceptions.py

```python
# app/core/exceptions.py
# ─────────────────────────────────────────────────────────────────
# Custom exception hierarchy for the risk analysis agent.
# Every exception type has a clear meaning and HTTP status code.
# ─────────────────────────────────────────────────────────────────

from fastapi import HTTPException


class RiskAgentError(Exception):
    """Base exception for all risk agent errors."""
    pass


class DatabaseConnectionError(RiskAgentError):
    """Cannot connect to collection database."""
    pass


class LocationNotFoundError(RiskAgentError):
    """Location not found in pakistan_locations table."""
    pass


class DisasterDataNotFoundError(RiskAgentError):
    """No disaster data found for given identifiers."""
    pass


class AgentExecutionError(RiskAgentError):
    """Agent failed to complete assessment."""
    pass


class InvalidInputError(RiskAgentError):
    """Input payload is invalid or incomplete."""
    pass


class ScoringError(RiskAgentError):
    """Error during risk score computation."""
    pass


def http_location_not_found(district: str) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail=f"Location not found for district: {district}"
    )


def http_agent_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=500,
        detail=f"Agent execution failed: {detail}"
    )


def http_unauthorized() -> HTTPException:
    return HTTPException(
        status_code=403,
        detail="Invalid or missing API key"
    )
```

---

## PART 4: DATABASE LAYER

### 4.1 app/database/connection.py

```python
# app/database/connection.py
# ─────────────────────────────────────────────────────────────────
# Async PostgreSQL connection pool using asyncpg.
# Connects to the DATA COLLECTION DATABASE in READ-ONLY mode.
# This agent never writes to the collection database.
# Pool is created at startup and closed at shutdown.
# ─────────────────────────────────────────────────────────────────

import asyncpg
from asyncpg import Pool
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Module-level pool — shared across all requests
_pool: Pool | None = None


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
        # Set Pakistan timezone on every connection
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
        f"Pool size: {settings.collection_db_pool_min}"
        f"-{settings.collection_db_pool_max}"
    )


async def _init_connection(conn) -> None:
    """
    Runs on every new connection from the pool.
    Sets timezone to Asia/Karachi for correct date calculations.
    """
    await conn.execute("SET timezone = 'Asia/Karachi'")


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
```

### 4.2 app/database/queries/location_queries.py

```python
# app/database/queries/location_queries.py
# ─────────────────────────────────────────────────────────────────
# All SQL queries for reading pakistan_locations and
# pakistan_infrastructure from the collection database.
# Queries are read-only. No INSERT, UPDATE, DELETE here.
# ─────────────────────────────────────────────────────────────────

GET_LOCATION_BY_DISTRICT = """
    SELECT
        location_id,
        location_key,
        location_name,
        local_name,
        location_tier,
        district,
        division,
        province,
        ST_X(coordinates::geometry)  AS longitude,
        ST_Y(coordinates::geometry)  AS latitude,
        elevation_m,
        population,
        population_density,
        flood_risk_zone,
        seismic_zone,
        heat_risk_zone,
        drought_risk_zone,
        infrastructure_quality,
        drainage_quality,
        building_stock,
        poll_priority,
        is_active
    FROM pakistan_locations
    WHERE district ILIKE $1
      AND province::TEXT = $2
      AND is_active = TRUE
    ORDER BY
        CASE location_tier
            WHEN 'tier_1_provincial_capital' THEN 1
            WHEN 'tier_2_district_headquarters' THEN 2
            ELSE 3
        END
    LIMIT 1
"""

# ─────────────────────────────────────────────────────────────────
# Get location by UUID (when location_id is known from breach)
# ─────────────────────────────────────────────────────────────────
GET_LOCATION_BY_ID = """
    SELECT
        location_id,
        location_key,
        location_name,
        local_name,
        location_tier,
        district,
        division,
        province,
        ST_X(coordinates::geometry)  AS longitude,
        ST_Y(coordinates::geometry)  AS latitude,
        elevation_m,
        population,
        population_density,
        flood_risk_zone,
        seismic_zone,
        heat_risk_zone,
        drought_risk_zone,
        infrastructure_quality,
        drainage_quality,
        building_stock,
        poll_priority,
        is_active
    FROM pakistan_locations
    WHERE location_id = $1
      AND is_active = TRUE
"""

# ─────────────────────────────────────────────────────────────────
# Get all locations within radius of a coordinate point.
# Uses PostGIS ST_DWithin for spatial filtering.
# $1 = longitude, $2 = latitude, $3 = radius in meters
# ─────────────────────────────────────────────────────────────────
GET_LOCATIONS_WITHIN_RADIUS = """
    SELECT
        location_id,
        location_name,
        district,
        province,
        population,
        population_density,
        flood_risk_zone,
        infrastructure_quality,
        drainage_quality,
        building_stock,
        ST_Distance(
            coordinates,
            ST_MakePoint($1, $2)::geography
        ) / 1000 AS distance_km
    FROM pakistan_locations
    WHERE ST_DWithin(
        coordinates,
        ST_MakePoint($1, $2)::geography,
        $3
    )
    AND is_active = TRUE
    ORDER BY distance_km ASC
"""
```

### 4.3 app/database/queries/infrastructure_queries.py

```python
# app/database/queries/infrastructure_queries.py
# ─────────────────────────────────────────────────────────────────
# SQL queries for reading pakistan_infrastructure table.
# Returns all critical assets within impact radius of disaster.
# ─────────────────────────────────────────────────────────────────

# Get all infrastructure within radius of disaster coordinates.
# $1 = longitude, $2 = latitude, $3 = radius in meters
GET_INFRASTRUCTURE_WITHIN_RADIUS = """
    SELECT
        asset_id,
        asset_name,
        asset_type,
        district,
        province,
        capacity,
        capacity_unit,
        vulnerability_score,
        vulnerability_level,
        is_seismic_resistant,
        is_flood_resistant,
        is_critical,
        serves_population,
        ST_Distance(
            coordinates,
            ST_MakePoint($1, $2)::geography
        ) / 1000 AS distance_km
    FROM pakistan_infrastructure
    WHERE ST_DWithin(
        coordinates,
        ST_MakePoint($1, $2)::geography,
        $3
    )
    AND is_active = TRUE
    ORDER BY
        is_critical DESC,
        distance_km ASC
"""

# ─────────────────────────────────────────────────────────────────
# Get hospital-specific data for medical capacity assessment
# ─────────────────────────────────────────────────────────────────
GET_HOSPITALS_WITHIN_RADIUS = """
    SELECT
        asset_id,
        asset_name,
        asset_type,
        capacity         AS beds,
        is_critical,
        is_flood_resistant,
        is_seismic_resistant,
        serves_population,
        vulnerability_level,
        ST_Distance(
            coordinates,
            ST_MakePoint($1, $2)::geography
        ) / 1000 AS distance_km
    FROM pakistan_infrastructure
    WHERE ST_DWithin(
        coordinates,
        ST_MakePoint($1, $2)::geography,
        $3
    )
    AND asset_type IN ('hospital', 'basic_health_unit')
    AND is_active = TRUE
    ORDER BY
        is_critical DESC,
        asset_type ASC,
        distance_km ASC
"""

# ─────────────────────────────────────────────────────────────────
# Get dam and barrage data (critical for flood cascading risk)
# ─────────────────────────────────────────────────────────────────
GET_DAMS_WITHIN_RADIUS = """
    SELECT
        asset_id,
        asset_name,
        asset_type,
        capacity,
        capacity_unit,
        vulnerability_score,
        is_critical,
        serves_population,
        ST_Distance(
            coordinates,
            ST_MakePoint($1, $2)::geography
        ) / 1000 AS distance_km
    FROM pakistan_infrastructure
    WHERE ST_DWithin(
        coordinates,
        ST_MakePoint($1, $2)::geography,
        $3
    )
    AND asset_type IN ('dam', 'barrage')
    AND is_active = TRUE
    ORDER BY distance_km ASC
"""

# ─────────────────────────────────────────────────────────────────
# Get evacuation and shelter infrastructure
# ─────────────────────────────────────────────────────────────────
GET_EVACUATION_CENTERS_WITHIN_RADIUS = """
    SELECT
        asset_id,
        asset_name,
        asset_type,
        capacity         AS shelter_capacity,
        is_flood_resistant,
        is_seismic_resistant,
        ST_Distance(
            coordinates,
            ST_MakePoint($1, $2)::geography
        ) / 1000 AS distance_km
    FROM pakistan_infrastructure
    WHERE ST_DWithin(
        coordinates,
        ST_MakePoint($1, $2)::geography,
        $3
    )
    AND asset_type IN ('flood_shelter', 'evacuation_center')
    AND is_active = TRUE
    ORDER BY distance_km ASC
"""
```

### 4.4 app/database/queries/disaster_data_queries.py

```python
# app/database/queries/disaster_data_queries.py
# ─────────────────────────────────────────────────────────────────
# SQL queries for reading time-series disaster data.
# Covers earthquake, flood gauge, and weather data.
# All queries are read-only against the collection database.
# ─────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────
# EARTHQUAKE QUERIES
# ─────────────────────────────────────────────────────────────────

GET_SEISMIC_EVENT_BY_USGS_ID = """
    SELECT
        event_id,
        usgs_event_id,
        usgs_event_url,
        magnitude,
        magnitude_type,
        magnitude_class,
        depth_km,
        depth_class,
        latitude,
        longitude,
        usgs_place,
        resolved_district,
        resolved_province,
        distance_to_nearest_km,
        felt_reports,
        cdi,
        mmi,
        tsunami_flag,
        usgs_alert_level,
        significance,
        station_count,
        azimuthal_gap_deg,
        rms_seconds,
        data_quality,
        contributing_networks,
        has_breach,
        breach_severity,
        initial_magnitude,
        magnitude_was_revised,
        usgs_last_updated_at,
        earthquake_time,
        first_seen_at,
        last_refreshed_at,
        raw_api_response
    FROM seismic_events
    WHERE usgs_event_id = $1
      AND data_quality != 'deleted'
"""

GET_RECENT_EARTHQUAKES_NEAR_LOCATION = """
    SELECT
        event_id,
        usgs_event_id,
        magnitude,
        magnitude_class,
        depth_km,
        depth_class,
        usgs_place,
        resolved_district,
        earthquake_time,
        data_quality,
        ST_Distance(
            coordinates,
            ST_MakePoint($1, $2)::geography
        ) / 1000 AS distance_km
    FROM seismic_events
    WHERE ST_DWithin(
        coordinates,
        ST_MakePoint($1, $2)::geography,
        $3
    )
    AND data_quality != 'deleted'
    AND earthquake_time >= now() - INTERVAL '5 days'
    ORDER BY earthquake_time DESC
    LIMIT 10
"""

# ─────────────────────────────────────────────────────────────────
# FLOOD QUERIES
# ─────────────────────────────────────────────────────────────────

GET_FLOOD_GAUGE_CURRENT_BY_ID = """
    SELECT
        fc.gauge_id,
        fc.google_gauge_id,
        fc.gauge_name,
        fc.river_name,
        fc.river_system,
        fc.district,
        fc.province,
        fc.reading_time,
        fc.current_level_m,
        fc.warning_level_m,
        fc.danger_level_m,
        fc.extreme_level_m,
        fc.pct_of_warning,
        fc.pct_of_danger,
        fc.pct_of_historical_max,
        fc.previous_level_m,
        fc.level_change_m,
        fc.rise_rate_m_per_hour,
        fc.river_trend,
        fc.hours_to_warning,
        fc.hours_to_danger,
        fc.flood_status,
        fc.has_breach,
        fc.breach_severity,
        fc.collected_at,
        -- Static registry data
        gr.river_system,
        gr.basin_name,
        gr.upstream_area_sqkm,
        gr.normal_level_m,
        gr.bankfull_level_m,
        gr.historical_max_m,
        gr.official_gauge_code
    FROM flood_gauge_current fc
    JOIN flood_gauge_registry gr ON gr.gauge_id = fc.gauge_id
    WHERE fc.gauge_id = $1
"""

GET_FLOOD_FORECASTS_FOR_GAUGE = """
    SELECT
        forecast_for_datetime,
        forecast_date,
        day_offset,
        forecast_horizon_h,
        forecast_issued_at,
        level_p10_m,
        level_p50_m,
        level_p90_m,
        prob_exceeds_warning_pct,
        prob_exceeds_danger_pct,
        prob_exceeds_extreme_pct,
        forecast_status,
        worst_case_status,
        has_forecast_breach,
        breach_severity
    FROM flood_gauge_forecasts
    WHERE gauge_id = $1
      AND forecast_for_datetime >= now()
    ORDER BY forecast_for_datetime ASC
"""

GET_NEARBY_FLOOD_GAUGES = """
    SELECT
        fc.gauge_id,
        fc.gauge_name,
        fc.river_name,
        fc.current_level_m,
        fc.pct_of_danger,
        fc.river_trend,
        fc.flood_status,
        gr.upstream_area_sqkm,
        ST_Distance(
            gr.coordinates,
            ST_MakePoint($1, $2)::geography
        ) / 1000 AS distance_km
    FROM flood_gauge_current fc
    JOIN flood_gauge_registry gr ON gr.gauge_id = fc.gauge_id
    WHERE ST_DWithin(
        gr.coordinates,
        ST_MakePoint($1, $2)::geography,
        $3
    )
    AND gr.is_active = TRUE
    ORDER BY distance_km ASC
    LIMIT 5
"""

# ─────────────────────────────────────────────────────────────────
# WEATHER QUERIES
# ─────────────────────────────────────────────────────────────────

GET_CURRENT_WEATHER_FOR_LOCATION = """
    SELECT
        location_id,
        location_name,
        district,
        province,
        forecast_for_datetime,
        day_offset,
        temp_c,
        temp_apparent_c,
        temp_dewpoint_c,
        precip_mm,
        precip_prob_pct,
        rain_mm,
        precip_3h_mm,
        precip_6h_mm,
        precip_12h_mm,
        precip_24h_mm,
        precip_72h_mm,
        wind_speed_kmh,
        wind_gusts_kmh,
        wind_direction_cardinal,
        humidity_pct,
        pressure_hpa,
        visibility_m,
        cloud_cover_pct,
        uv_index,
        cape_jkg,
        weather_code,
        weather_condition,
        weather_description,
        is_daytime,
        flag_extreme_heat,
        flag_heatwave,
        flag_heavy_rain,
        flag_very_heavy_rain,
        flag_storm,
        flag_severe_storm,
        flag_cold_wave,
        flag_dust_storm,
        flag_dense_fog,
        has_breach,
        breach_severity,
        breach_metric,
        breach_observed_value,
        last_updated_at
    FROM weather_hourly_window
    WHERE location_id = $1
      AND forecast_for_datetime <= now()
      AND day_offset = 0
    ORDER BY forecast_for_datetime DESC
    LIMIT 1
"""

GET_WEATHER_DAILY_SUMMARY_5DAY = """
    SELECT
        summary_date,
        day_offset,
        temp_max_c,
        temp_min_c,
        feels_like_max_c,
        feels_like_min_c,
        precip_total_mm,
        rain_total_mm,
        precip_hours,
        precip_prob_max_pct,
        wind_speed_max_kmh,
        wind_gusts_max_kmh,
        dominant_condition,
        uv_index_max,
        sunrise_at,
        sunset_at,
        daylight_hours,
        flag_extreme_heat_day,
        flag_heatwave_day,
        flag_heavy_rain_day,
        flag_storm_day,
        flag_cold_wave_day,
        worst_breach_severity,
        last_updated_at
    FROM weather_daily_summaries
    WHERE location_id = $1
    ORDER BY day_offset ASC
"""

GET_HOURLY_FORECAST_NEXT_72H = """
    SELECT
        forecast_for_datetime,
        day_offset,
        temp_c,
        temp_apparent_c,
        precip_mm,
        precip_24h_mm,
        precip_72h_mm,
        wind_speed_kmh,
        wind_gusts_kmh,
        humidity_pct,
        cape_jkg,
        weather_condition,
        flag_extreme_heat,
        flag_heavy_rain,
        flag_storm,
        flag_severe_storm,
        has_breach,
        breach_severity
    FROM weather_hourly_window
    WHERE location_id = $1
      AND forecast_for_datetime >= now()
      AND forecast_for_datetime <= now() + INTERVAL '72 hours'
    ORDER BY forecast_for_datetime ASC
"""
```

---

## PART 5: INPUT AND OUTPUT MODELS

### 5.1 app/models/input_models.py

```python
# app/models/input_models.py
# ─────────────────────────────────────────────────────────────────
# Pydantic models for validating incoming breach payload
# from the main ClimaSync system.
# ─────────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class DisasterKind(str, Enum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FLASH_FLOOD = "flash_flood"
    HEATWAVE = "heatwave"
    CYCLONE = "cyclone"
    HEAVY_RAIN = "heavy_rain"
    DROUGHT = "drought"
    LANDSLIDE = "landslide"
    DUST_STORM = "dust_storm"
    COLD_WAVE = "cold_wave"


class BreachSeverity(str, Enum):
    WATCH = "watch"
    WARNING = "warning"
    EMERGENCY = "emergency"
    EXTREME = "extreme"


class Province(str, Enum):
    PUNJAB = "punjab"
    SINDH = "sindh"
    KPK = "khyber_pakhtunkhwa"
    BALOCHISTAN = "balochistan"
    GB = "gilgit_baltistan"
    AJK = "azad_kashmir"
    ICT = "islamabad_capital_territory"


class SourceAPI(str, Enum):
    USGS = "usgs"
    OPEN_METEO = "open_meteo"
    GOOGLE_FLOOD_HUB = "google_flood_hub"


class BreachPayload(BaseModel):
    """
    Incoming breach payload from main ClimaSync system.
    Sent by admin portal when triggering risk analysis.
    All fields except optional ones are required.
    """
    breach_id: str = Field(..., description="UUID of breach record")
    disaster_kind: DisasterKind
    location_name: str = Field(..., min_length=1)
    district: str = Field(..., min_length=1)
    province: Province
    latitude: float = Field(..., ge=23.0, le=38.0)
    longitude: float = Field(..., ge=60.0, le=78.0)
    observed_value: float
    threshold_value: float
    breach_severity: BreachSeverity
    metric_name: str = Field(..., min_length=1)
    observation_time: str
    is_forecast_breach: bool = False
    forecast_horizon_h: Optional[int] = None
    source_api: SourceAPI

    # Source-specific identifiers (at least one required)
    gauge_id: Optional[str] = None
    usgs_event_id: Optional[str] = None
    weather_location_id: Optional[str] = None

    @field_validator("forecast_horizon_h")
    @classmethod
    def validate_forecast_horizon(
        cls, v, values
    ):
        if values.data.get("is_forecast_breach") and v is None:
            raise ValueError(
                "forecast_horizon_h required when "
                "is_forecast_breach is True"
            )
        return v
```

### 5.2 app/models/output_models.py

```python
# app/models/output_models.py
# ─────────────────────────────────────────────────────────────────
# Complete Pydantic output schema for the risk assessment report.
# Every field documented. Precaution Definer Agent reads this.
# ─────────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class DataConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SituationTrajectory(str, Enum):
    IMPROVING = "Improving"
    STABLE = "Stable"
    WORSENING = "Worsening"
    RAPIDLY_WORSENING = "Rapidly Worsening"


class ResponseUrgency(str, Enum):
    MONITOR = "Monitor"
    PREPARE = "Prepare"
    RESPOND = "Respond"
    EMERGENCY = "Emergency"


# ── TERRAIN ────────────────────────────────────────────────────────

class TerrainAssessment(BaseModel):
    terrain_type: str
    # mountain / highland / urban / riverine_plain /
    # agricultural_plain / desert / coastal
    terrain_source: str
    # "database_derived" or "web_search"
    terrain_vulnerability_score: int = Field(..., ge=0, le=100)
    terrain_multiplier: float
    terrain_implications: list[str]
    slope_description: Optional[str] = None
    soil_type: Optional[str] = None
    vegetation_cover: Optional[str] = None


# ── HAZARD SEVERITY ────────────────────────────────────────────────

class HazardSeverityScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    base_score: int
    modifiers_applied: list[str]
    key_metric_name: str
    key_metric_value: str
    secondary_hazards_identified: list[str]
    justification: str


# ── EXPOSURE ───────────────────────────────────────────────────────

class PopulationBreakdown(BaseModel):
    total_population: int
    population_source: str
    population_density_per_sqkm: Optional[float]
    estimated_directly_affected: int
    estimation_method: str
    vulnerable_groups: dict[str, int]
    poverty_rate_pct: float
    poverty_source: str
    outdoor_workers_estimate: Optional[int] = None


class InfrastructureAtRisk(BaseModel):
    hospitals_count: int
    hospital_beds_total: int
    hospital_beds_per_1000_population: float
    critical_hospitals: list[str]
    schools_count: int
    estimated_students_at_risk: int
    bridges_count: int
    critical_bridges: list[str]
    dams_count: int
    barrages_count: int
    dam_failure_risk: bool
    dam_failure_risk_reason: Optional[str]
    evacuation_centers_count: int
    evacuation_capacity_total: int
    evacuation_coverage_pct: float
    power_stations_at_risk: int
    water_treatment_at_risk: int
    total_critical_assets: int
    impact_radius_km_used: float


class ExposureScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    population_score: int
    infrastructure_score: int
    population_breakdown: PopulationBreakdown
    infrastructure_at_risk: InfrastructureAtRisk
    justification: str


# ── VULNERABILITY ──────────────────────────────────────────────────

class VulnerabilityScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    building_vulnerability_score: int
    building_stock_type: str
    building_stock_source: str
    kutcha_percentage_estimate: Optional[float]
    drainage_vulnerability_score: int
    drainage_quality_level: str
    infrastructure_quality_score: int
    poverty_vulnerability_score: int
    terrain_vulnerability_score: int
    component_scores: dict[str, int]
    justification: str


# ── ESCALATION ─────────────────────────────────────────────────────

class EscalationScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    is_worsening: bool
    trajectory_description: str
    current_trajectory_score: int
    secondary_disaster_score: int
    secondary_disasters_possible: list[str]
    escalation_probability_pct: float
    hours_until_peak_estimate: Optional[float]
    peak_estimate_basis: str
    justification: str


# ── RESPONSE CAPACITY ──────────────────────────────────────────────

class ResponseCapacityScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    # Higher score = lower capacity = more vulnerable
    medical_capacity_score: int
    evacuation_capacity_score: int
    road_access_score: int
    ngo_presence_score: int
    road_status_description: str
    ngo_presence_description: str
    nearest_major_hospital_km: Optional[float]
    response_time_estimate_hours: Optional[float]
    justification: str


# ── WEB SEARCH FINDINGS ────────────────────────────────────────────

class WebSearchFinding(BaseModel):
    query_used: str
    key_findings: str
    sources_cited: list[str]
    confidence: str


class WebSearchFindings(BaseModel):
    terrain_geography: WebSearchFinding
    demographics_poverty: WebSearchFinding
    historical_disaster_context: WebSearchFinding
    current_ground_situation: WebSearchFinding
    disaster_specific_findings: list[WebSearchFinding]


# ── IMPACT ESTIMATES ───────────────────────────────────────────────

class ImpactEstimates(BaseModel):
    estimated_population_affected: int
    estimation_confidence: DataConfidence
    estimated_deaths_range: str
    death_risk_level: str
    estimated_displaced_persons: int
    displacement_duration_estimate: str
    estimated_economic_damage_pkr: str
    estimated_economic_damage_usd: str
    economic_damage_confidence: DataConfidence
    agricultural_land_at_risk_acres: Optional[int]
    crop_loss_probability_pct: Optional[float]
    livestock_at_risk_description: Optional[str]


# ── COMPLETE REPORT ────────────────────────────────────────────────

class RiskAssessmentReport(BaseModel):

    # Identification
    assessment_id: str
    breach_id: str
    disaster_kind: str
    breach_severity_received: str
    location_name: str
    district: str
    province: str
    latitude: float
    longitude: float
    observation_time: str
    is_forecast_breach: bool
    forecast_horizon_h: Optional[int]
    assessment_timestamp: str
    agent_version: str = "risk_analysis_v2.0"

    # Terrain
    terrain_assessment: TerrainAssessment

    # Five dimension scores
    hazard_severity: HazardSeverityScore
    exposure: ExposureScore
    vulnerability: VulnerabilityScore
    escalation_risk: EscalationScore
    response_capacity: ResponseCapacityScore

    # Composite result
    score_breakdown: dict[str, float]
    composite_score_before_terrain: float
    terrain_multiplier_applied: float
    composite_risk_score: float
    override_applied: bool
    override_reason: Optional[str]
    risk_level: RiskLevel
    risk_level_justification: str

    # Impact
    impact_estimates: ImpactEstimates

    # Situation
    situation_trajectory: SituationTrajectory
    escalation_triggers: list[str]

    # Web search
    web_search_findings: WebSearchFindings

    # Handoff to Precaution Definer
    recommended_response_urgency: ResponseUrgency
    critical_actions_needed: list[str]
    time_sensitive_actions: list[str]

    # Data quality
    data_confidence: DataConfidence
    data_gaps: list[str]
    assumptions_made: list[str]
```

---

## PART 6: AGENT TOOLS

### 6.1 app/agent/tools/location_tool.py

```python
# app/agent/tools/location_tool.py
# ─────────────────────────────────────────────────────────────────
# Tool 1: get_location_data
# Reads pakistan_locations from collection database.
# Returns complete location vulnerability context.
# ─────────────────────────────────────────────────────────────────

import json
from agents import function_tool
from app.database.connection import get_pool
from app.database.queries.location_queries import (
    GET_LOCATION_BY_DISTRICT,
    GET_LOCATION_BY_ID,
    GET_LOCATIONS_WITHIN_RADIUS,
)
from app.core.logger import setup_logger

logger = setup_logger(__name__)


@function_tool
async def get_location_data(
    district: str,
    province: str,
    location_id: str | None = None,
) -> str:
    """
    Retrieves complete location data from the pakistan_locations
    table in the collection database.

    Returns population, vulnerability levels, risk zones,
    infrastructure quality, drainage quality, building stock,
    and elevation data for the affected location.

    This data is used to assess exposure and vulnerability
    dimensions of the risk assessment.

    Args:
        district: Name of the affected district in Pakistan
        province: Province enum value (punjab, sindh, etc.)
        location_id: Optional UUID if known from breach payload

    Returns:
        JSON string with complete location data
    """
    pool = get_pool()

    try:
        async with pool.acquire() as conn:

            # Try by ID first if provided
            if location_id:
                row = await conn.fetchrow(
                    GET_LOCATION_BY_ID, location_id
                )
            else:
                row = await conn.fetchrow(
                    GET_LOCATION_BY_DISTRICT,
                    district,
                    province
                )

            if not row:
                logger.warning(
                    f"Location not found: {district}, {province}. "
                    f"Attempting radius search."
                )
                return json.dumps({
                    "found": False,
                    "district": district,
                    "province": province,
                    "message": (
                        "Location not found in database. "
                        "Use web search to find population "
                        "and vulnerability data for this district."
                    )
                })

            result = dict(row)
            result["found"] = True

            # Add computed fields for agent convenience
            if result.get("population") and result.get(
                "population_density"
            ):
                result["population_note"] = (
                    f"Population: {result['population']:,} people "
                    f"at density "
                    f"{result['population_density']:.1f}/km²"
                )

            logger.info(
                f"Location data retrieved: {district}, {province}. "
                f"Population: {result.get('population', 'unknown')}"
            )

            return json.dumps(result, default=str)

    except Exception as e:
        logger.error(f"Location tool error: {e}")
        return json.dumps({
            "found": False,
            "error": str(e),
            "message": (
                "Database error. Use web search for location data."
            )
        })
```

### 6.2 app/agent/tools/infrastructure_tool.py

```python
# app/agent/tools/infrastructure_tool.py
# ─────────────────────────────────────────────────────────────────
# Tool 2: get_infrastructure_at_risk
# Finds all critical infrastructure within disaster impact radius.
# Returns hospitals, schools, bridges, dams, evacuation centers.
# ─────────────────────────────────────────────────────────────────

import json
from agents import function_tool
from app.database.connection import get_pool
from app.database.queries.infrastructure_queries import (
    GET_INFRASTRUCTURE_WITHIN_RADIUS,
    GET_HOSPITALS_WITHIN_RADIUS,
    GET_DAMS_WITHIN_RADIUS,
    GET_EVACUATION_CENTERS_WITHIN_RADIUS,
)
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Impact radius by disaster type and magnitude
IMPACT_RADIUS_KM = {
    "earthquake": {
        "default": 25,
        "M4-5": 15,
        "M5-6": 25,
        "M6-7": 40,
        "M7+": 60,
    },
    "flood": 30,
    "flash_flood": 20,
    "heatwave": 50,  # entire district essentially
    "heavy_rain": 20,
    "cyclone": 80,
    "cold_wave": 50,
    "dust_storm": 30,
    "landslide": 15,
    "drought": 100,
}


def get_radius_meters(
    disaster_kind: str,
    magnitude: float | None = None
) -> float:
    """
    Determines impact radius in meters based on disaster type
    and magnitude for earthquakes.
    """
    if disaster_kind == "earthquake" and magnitude:
        if magnitude < 5.0:
            km = IMPACT_RADIUS_KM["earthquake"]["M4-5"]
        elif magnitude < 6.0:
            km = IMPACT_RADIUS_KM["earthquake"]["M5-6"]
        elif magnitude < 7.0:
            km = IMPACT_RADIUS_KM["earthquake"]["M6-7"]
        else:
            km = IMPACT_RADIUS_KM["earthquake"]["M7+"]
    else:
        radius = IMPACT_RADIUS_KM.get(disaster_kind, 25)
        km = radius if isinstance(radius, (int, float)) else 25

    return km * 1000  # Convert to meters for PostGIS


@function_tool
async def get_infrastructure_at_risk(
    longitude: float,
    latitude: float,
    disaster_kind: str,
    magnitude: float | None = None,
) -> str:
    """
    Finds all critical infrastructure assets within the impact
    radius of the disaster location.

    Queries pakistan_infrastructure table from collection database.
    Returns categorized list of hospitals, schools, bridges,
    dams, barrages, and evacuation centers with their capacity
    and vulnerability information.

    Args:
        longitude: Disaster epicenter/location longitude
        latitude: Disaster epicenter/location latitude
        disaster_kind: Type of disaster for radius calculation
        magnitude: Earthquake magnitude if applicable

    Returns:
        JSON string with categorized infrastructure inventory
    """
    pool = get_pool()
    radius_m = get_radius_meters(disaster_kind, magnitude)
    radius_km = radius_m / 1000

    try:
        async with pool.acquire() as conn:

            # Get all infrastructure
            all_assets = await conn.fetch(
                GET_INFRASTRUCTURE_WITHIN_RADIUS,
                longitude, latitude, radius_m
            )

            # Get specific categories
            hospitals = await conn.fetch(
                GET_HOSPITALS_WITHIN_RADIUS,
                longitude, latitude, radius_m
            )

            dams = await conn.fetch(
                GET_DAMS_WITHIN_RADIUS,
                longitude, latitude, radius_m
            )

            shelters = await conn.fetch(
                GET_EVACUATION_CENTERS_WITHIN_RADIUS,
                longitude, latitude, radius_m
            )

        # Process results
        hospital_list = [dict(h) for h in hospitals]
        dam_list = [dict(d) for d in dams]
        shelter_list = [dict(s) for s in shelters]
        all_assets_list = [dict(a) for a in all_assets]

        # Categorize by type
        categories: dict = {
            "hospital": [],
            "basic_health_unit": [],
            "school": [],
            "bridge": [],
            "dam": [],
            "barrage": [],
            "power_station": [],
            "water_treatment": [],
            "airport": [],
            "flood_shelter": [],
            "evacuation_center": [],
        }

        total_hospital_beds = 0
        total_school_students = 0
        total_evacuation_capacity = 0
        critical_asset_names = []

        for asset in all_assets_list:
            asset_type = asset.get("asset_type", "unknown")
            if asset_type in categories:
                categories[asset_type].append(asset)

            if asset.get("is_critical"):
                critical_asset_names.append(
                    asset.get("asset_name", "Unknown")
                )

            if asset_type in ("hospital", "basic_health_unit"):
                total_hospital_beds += asset.get("capacity") or 0

            if asset_type == "school":
                total_school_students += (
                    asset.get("serves_population") or 0
                )

            if asset_type in (
                "flood_shelter", "evacuation_center"
            ):
                total_evacuation_capacity += (
                    asset.get("capacity") or 0
                )

        result = {
            "impact_radius_km": radius_km,
            "total_assets_found": len(all_assets_list),
            "critical_assets_count": len(critical_asset_names),
            "critical_asset_names": critical_asset_names,

            # Hospitals
            "hospitals_count": len(
                categories["hospital"]
            ),
            "basic_health_units_count": len(
                categories["basic_health_unit"]
            ),
            "total_hospital_beds": total_hospital_beds,
            "hospitals": hospital_list,

            # Schools
            "schools_count": len(categories["school"]),
            "estimated_students_at_risk": total_school_students,

            # Bridges
            "bridges_count": len(categories["bridge"]),
            "bridges": [
                {
                    "name": b["asset_name"],
                    "distance_km": b["distance_km"],
                    "is_critical": b["is_critical"],
                }
                for b in categories["bridge"]
            ],

            # Dams and barrages
            "dams_count": len(categories["dam"]),
            "barrages_count": len(categories["barrage"]),
            "dam_failure_risk": len(dam_list) > 0,
            "dams_and_barrages": dam_list,

            # Power
            "power_stations_count": len(
                categories["power_station"]
            ),

            # Water
            "water_treatment_count": len(
                categories["water_treatment"]
            ),

            # Evacuation
            "evacuation_centers_count": len(
                categories["flood_shelter"]
            ) + len(categories["evacuation_center"]),
            "total_evacuation_capacity": (
                total_evacuation_capacity
            ),
            "shelters": shelter_list,
        }

        logger.info(
            f"Infrastructure scan: radius={radius_km}km, "
            f"assets={len(all_assets_list)}, "
            f"hospitals={result['hospitals_count']}, "
            f"dams={result['dams_count']}"
        )

        return json.dumps(result, default=str)

    except Exception as e:
        logger.error(f"Infrastructure tool error: {e}")
        return json.dumps({
            "error": str(e),
            "impact_radius_km": radius_km,
            "message": (
                "Database error reading infrastructure. "
                "Note this as a data gap."
            )
        })
```

### 6.3 app/agent/tools/disaster_data_tool.py

```python
# app/agent/tools/disaster_data_tool.py
# ─────────────────────────────────────────────────────────────────
# Tool 3: get_current_disaster_data
# Reads time-series tables based on disaster type.
# Earthquake → seismic_events
# Flood → flood_gauge_current + flood_gauge_forecasts
# Weather → weather_hourly_window + weather_daily_summaries
# ─────────────────────────────────────────────────────────────────

import json
from agents import function_tool
from app.database.connection import get_pool
from app.database.queries.disaster_data_queries import (
    GET_SEISMIC_EVENT_BY_USGS_ID,
    GET_RECENT_EARTHQUAKES_NEAR_LOCATION,
    GET_FLOOD_GAUGE_CURRENT_BY_ID,
    GET_FLOOD_FORECASTS_FOR_GAUGE,
    GET_NEARBY_FLOOD_GAUGES,
    GET_CURRENT_WEATHER_FOR_LOCATION,
    GET_WEATHER_DAILY_SUMMARY_5DAY,
    GET_HOURLY_FORECAST_NEXT_72H,
)
from app.core.logger import setup_logger

logger = setup_logger(__name__)


@function_tool
async def get_current_disaster_data(
    disaster_kind: str,
    usgs_event_id: str | None = None,
    gauge_id: str | None = None,
    weather_location_id: str | None = None,
    longitude: float | None = None,
    latitude: float | None = None,
) -> str:
    """
    Retrieves the latest disaster measurement data from the
    collection database based on disaster type.

    For EARTHQUAKE: reads seismic_events table using usgs_event_id
    For FLOOD: reads flood_gauge_current and flood_gauge_forecasts
    For WEATHER disasters (heatwave, heavy_rain, storm, cold_wave,
      dust_storm): reads weather_hourly_window and
      weather_daily_summaries

    Args:
        disaster_kind: earthquake/flood/flash_flood/heatwave/
                       heavy_rain/cyclone/cold_wave/dust_storm
        usgs_event_id: USGS event ID for earthquake events
        gauge_id: Google Flood Hub gauge UUID for flood events
        weather_location_id: Location UUID for weather events
        longitude: Longitude for nearby gauge/event searches
        latitude: Latitude for nearby gauge/event searches

    Returns:
        JSON string with complete current disaster measurements
    """
    pool = get_pool()

    try:
        async with pool.acquire() as conn:

            # ── EARTHQUAKE ────────────────────────────────────────
            if disaster_kind == "earthquake":
                if not usgs_event_id:
                    return json.dumps({
                        "error": "usgs_event_id required for earthquake",
                        "disaster_kind": disaster_kind
                    })

                event = await conn.fetchrow(
                    GET_SEISMIC_EVENT_BY_USGS_ID,
                    usgs_event_id
                )

                if not event:
                    return json.dumps({
                        "found": False,
                        "usgs_event_id": usgs_event_id,
                        "message": "Event not in database yet"
                    })

                # Get nearby recent earthquakes for
                # aftershock context
                nearby = []
                if longitude and latitude:
                    nearby_rows = await conn.fetch(
                        GET_RECENT_EARTHQUAKES_NEAR_LOCATION,
                        longitude, latitude, 100000  # 100km
                    )
                    nearby = [dict(r) for r in nearby_rows]

                result = dict(event)
                result["nearby_recent_earthquakes"] = nearby
                result["disaster_kind"] = "earthquake"

                # Remove raw_api_response to keep response clean
                result.pop("raw_api_response", None)

                return json.dumps(result, default=str)

            # ── FLOOD ─────────────────────────────────────────────
            elif disaster_kind in ("flood", "flash_flood"):
                if not gauge_id:
                    return json.dumps({
                        "error": "gauge_id required for flood",
                        "disaster_kind": disaster_kind
                    })

                current = await conn.fetchrow(
                    GET_FLOOD_GAUGE_CURRENT_BY_ID,
                    gauge_id
                )

                forecasts = await conn.fetch(
                    GET_FLOOD_FORECASTS_FOR_GAUGE,
                    gauge_id
                )

                # Get nearby gauges for context
                nearby_gauges = []
                if longitude and latitude:
                    nearby_rows = await conn.fetch(
                        GET_NEARBY_FLOOD_GAUGES,
                        longitude, latitude, 200000  # 200km
                    )
                    nearby_gauges = [
                        dict(r) for r in nearby_rows
                    ]

                # Organize forecasts by horizon
                forecast_list = [dict(f) for f in forecasts]

                # Find 24h, 48h, 72h forecasts
                forecast_24h = next(
                    (f for f in forecast_list
                     if 22 <= f.get("forecast_horizon_h", 0) <= 26),
                    None
                )
                forecast_48h = next(
                    (f for f in forecast_list
                     if 46 <= f.get("forecast_horizon_h", 0) <= 50),
                    None
                )
                forecast_72h = next(
                    (f for f in forecast_list
                     if 70 <= f.get("forecast_horizon_h", 0) <= 74),
                    None
                )

                result = {
                    "disaster_kind": disaster_kind,
                    "current_gauge": dict(current) if current else None,
                    "forecast_24h": forecast_24h,
                    "forecast_48h": forecast_48h,
                    "forecast_72h": forecast_72h,
                    "all_forecasts_count": len(forecast_list),
                    "nearby_gauges": nearby_gauges,
                }

                if current:
                    # Remove raw response
                    result["current_gauge"].pop(
                        "raw_api_response", None
                    )

                return json.dumps(result, default=str)

            # ── WEATHER DISASTERS ──────────────────────────────────
            elif disaster_kind in (
                "heatwave", "heavy_rain", "cyclone",
                "cold_wave", "dust_storm", "landslide",
                "drought"
            ):
                if not weather_location_id:
                    return json.dumps({
                        "error": (
                            "weather_location_id required for "
                            "weather disasters"
                        ),
                        "disaster_kind": disaster_kind
                    })

                current_weather = await conn.fetchrow(
                    GET_CURRENT_WEATHER_FOR_LOCATION,
                    weather_location_id
                )

                daily_summaries = await conn.fetch(
                    GET_WEATHER_DAILY_SUMMARY_5DAY,
                    weather_location_id
                )

                hourly_72h = await conn.fetch(
                    GET_HOURLY_FORECAST_NEXT_72H,
                    weather_location_id
                )

                daily_list = [dict(d) for d in daily_summaries]
                hourly_list = [dict(h) for h in hourly_72h]

                # Compute heatwave duration
                consecutive_heat_days = 0
                for day in daily_list:
                    if day.get("flag_heatwave_day"):
                        consecutive_heat_days += 1
                    else:
                        break

                # Find peak conditions in 72h
                peak_temp = max(
                    (h.get("temp_c") or 0 for h in hourly_list),
                    default=0
                )
                peak_precip_24h = max(
                    (h.get("precip_24h_mm") or 0
                     for h in hourly_list),
                    default=0
                )
                peak_cape = max(
                    (h.get("cape_jkg") or 0 for h in hourly_list),
                    default=0
                )
                peak_wind_gusts = max(
                    (h.get("wind_gusts_kmh") or 0
                     for h in hourly_list),
                    default=0
                )

                result = {
                    "disaster_kind": disaster_kind,
                    "current_weather": (
                        dict(current_weather)
                        if current_weather else None
                    ),
                    "daily_summaries_5day": daily_list,
                    "hourly_forecast_count": len(hourly_list),
                    "computed_insights": {
                        "consecutive_heatwave_days": (
                            consecutive_heat_days
                        ),
                        "peak_temp_72h_c": peak_temp,
                        "peak_precip_24h_72h_mm": peak_precip_24h,
                        "peak_cape_jkg": peak_cape,
                        "peak_wind_gusts_kmh": peak_wind_gusts,
                    }
                }

                return json.dumps(result, default=str)

            else:
                return json.dumps({
                    "error": f"Unknown disaster_kind: {disaster_kind}"
                })

    except Exception as e:
        logger.error(f"Disaster data tool error: {e}")
        return json.dumps({
            "error": str(e),
            "disaster_kind": disaster_kind,
            "message": "Database error. Note as data gap."
        })
```

### 6.4 app/agent/tools/web_search_tool.py

```python
# app/agent/tools/web_search_tool.py
# ─────────────────────────────────────────────────────────────────
# Tool 4: web_search
# Uses OpenAI built-in web search capability.
# Provides real-time internet data for gaps not in database.
# ─────────────────────────────────────────────────────────────────

from agents import WebSearchTool

# OpenAI Agents SDK provides WebSearchTool as a built-in.
# Simply instantiate and include in the agent's tools list.
# The agent decides when and what to search based on system prompt.

web_search_tool = WebSearchTool()
```

---

## PART 6: SCORING ENGINE

### 6.5 app/agent/scoring/hazard_scorer.py

```python
# app/agent/scoring/hazard_scorer.py
# ─────────────────────────────────────────────────────────────────
# Deterministic hazard severity scoring for all disaster types.
# These functions are called by the agent through the system prompt
# instructions. The agent calls tools, gets data, then applies
# these scoring rules as instructed in the system prompt.
# ─────────────────────────────────────────────────────────────────

def score_earthquake_hazard(
    magnitude: float,
    depth_km: float | None,
    magnitude_was_revised: bool,
    initial_magnitude: float | None,
    usgs_alert_level: str | None,
    significance: int | None,
    felt_reports: int | None,
    tsunami_flag: bool,
    azimuthal_gap_deg: float | None,
    terrain_type: str,
    dam_within_50km: bool,
) -> tuple[int, list[str]]:
    """
    Returns (score 0-100, list of modifiers applied)
    """
    modifiers = []

    # Base score from magnitude
    if magnitude < 4.0:
        base = 10
    elif magnitude < 5.0:
        base = 25
    elif magnitude < 6.0:
        base = 50
    elif magnitude < 7.0:
        base = 75
    elif magnitude < 8.0:
        base = 90
    else:
        base = 100

    score = base
    modifiers.append(f"base_score={base} from M{magnitude}")

    # Depth modifier
    if depth_km is not None:
        if depth_km <= 70:
            score += 20
            modifiers.append(
                f"shallow_depth={depth_km}km → +20"
            )
        elif depth_km <= 300:
            score += 8
            modifiers.append(
                f"intermediate_depth={depth_km}km → +8"
            )

    # Magnitude revision
    if magnitude_was_revised and initial_magnitude:
        if magnitude > initial_magnitude:
            score += 10
            modifiers.append(
                f"magnitude_revised_UP from "
                f"{initial_magnitude} → +10"
            )
        else:
            score -= 5
            modifiers.append(
                f"magnitude_revised_DOWN → -5"
            )

    # USGS alert level override
    if usgs_alert_level == "red":
        score = max(score, 90)
        modifiers.append("usgs_alert=red → min 90")
    elif usgs_alert_level == "orange":
        score = max(score, 70)
        modifiers.append("usgs_alert=orange → min 70")

    # Significance
    if significance and significance > 800:
        score += 10
        modifiers.append(f"significance={significance} → +10")

    # Felt reports
    if felt_reports and felt_reports > 1000:
        score += 5
        modifiers.append(
            f"felt_reports={felt_reports} → +5"
        )

    # Tsunami
    if tsunami_flag:
        score += 25
        modifiers.append("tsunami_flag=TRUE → +25")

    # Location quality
    if azimuthal_gap_deg and azimuthal_gap_deg > 180:
        modifiers.append(
            f"azimuthal_gap={azimuthal_gap_deg}° "
            f"→ location_estimate_uncertain (no score change)"
        )

    # Secondary hazards
    if terrain_type in ("mountain", "highland") and magnitude >= 5.5:
        score += 15
        modifiers.append(
            "mountain_terrain + M5.5+ → landslide_risk → +15"
        )

    if dam_within_50km and magnitude >= 5.0:
        score += 20
        modifiers.append(
            "dam_within_50km + M5.0+ → dam_failure_risk → +20"
        )

    return min(score, 100), modifiers


def score_flood_hazard(
    pct_of_danger: float | None,
    river_trend: str,
    hours_to_danger: float | None,
    forecast_72h_danger_prob: float | None,
    upstream_area_sqkm: float | None,
    pct_of_historical_max: float | None,
    terrain_type: str,
    soil_saturated: bool,
) -> tuple[int, list[str]]:
    """
    Returns (score 0-100, list of modifiers applied)
    """
    modifiers = []

    if pct_of_danger is None:
        return 20, ["pct_of_danger_unknown → default 20"]

    # Base score from percentage of danger level
    if pct_of_danger < 50:
        base = 10
    elif pct_of_danger < 70:
        base = 25
    elif pct_of_danger < 85:
        base = 45
    elif pct_of_danger < 100:
        base = 65
    elif pct_of_danger < 120:
        base = 80
    else:
        base = 95

    score = base
    modifiers.append(
        f"base={base} from pct_of_danger={pct_of_danger:.1f}%"
    )

    # River trend
    trend_modifiers = {
        "rapidly_rising": (20, "+20"),
        "rising": (10, "+10"),
        "stable": (0, "+0"),
        "falling": (-10, "-10"),
        "rapidly_falling": (-15, "-15"),
    }
    delta, label = trend_modifiers.get(
        river_trend, (0, "unknown")
    )
    score += delta
    modifiers.append(f"river_trend={river_trend} → {label}")

    # Time to danger
    if hours_to_danger is not None:
        if hours_to_danger < 6:
            score += 15
            modifiers.append(
                f"hours_to_danger={hours_to_danger:.1f}h → +15"
            )
        elif hours_to_danger < 12:
            score += 8
            modifiers.append(
                f"hours_to_danger={hours_to_danger:.1f}h → +8"
            )

    # 72h forecast
    if forecast_72h_danger_prob is not None:
        if forecast_72h_danger_prob > 70:
            score += 15
            modifiers.append(
                f"72h_danger_prob={forecast_72h_danger_prob}% → +15"
            )
        elif forecast_72h_danger_prob > 40:
            score += 8
            modifiers.append(
                f"72h_danger_prob={forecast_72h_danger_prob}% → +8"
            )

    # Upstream area
    if upstream_area_sqkm:
        if upstream_area_sqkm > 200000:
            score += 12
            modifiers.append(
                f"upstream_area={upstream_area_sqkm:.0f}km² → +12"
            )
        elif upstream_area_sqkm > 100000:
            score += 8
            modifiers.append(
                f"upstream_area={upstream_area_sqkm:.0f}km² → +8"
            )

    # Historical max comparison
    if pct_of_historical_max and pct_of_historical_max > 90:
        score += 15
        modifiers.append(
            f"pct_of_historical_max="
            f"{pct_of_historical_max:.1f}% → +15"
        )

    # Terrain
    if terrain_type == "mountain":
        score += 15
        modifiers.append("mountain_terrain → flash_flood → +15")

    # Soil saturation
    if soil_saturated:
        score += 10
        modifiers.append("soil_saturated → +10")

    return min(score, 100), modifiers


def score_heatwave_hazard(
    temp_max_c: float | None,
    temp_apparent_c: float | None,
    temp_dewpoint_c: float | None,
    humidity_pct: float | None,
    consecutive_days: int,
    night_temp_min: float | None,
    electricity_outage_hours: float | None,
    water_shortage: bool,
) -> tuple[int, list[str]]:
    """
    Returns (score 0-100, list of modifiers applied)
    """
    modifiers = []

    if temp_max_c is None:
        return 20, ["temp_max_unknown → default 20"]

    # Use apparent temperature if higher
    effective_temp = temp_max_c
    if temp_apparent_c and temp_apparent_c > temp_max_c:
        effective_temp = temp_apparent_c
        modifiers.append(
            f"using_apparent_temp={temp_apparent_c}°C "
            f"(higher than actual {temp_max_c}°C)"
        )

    # Base score
    if effective_temp < 40:
        base = 5
    elif effective_temp < 44:
        base = 25
    elif effective_temp < 47:
        base = 50
    elif effective_temp < 50:
        base = 70
    elif effective_temp < 53:
        base = 85
    else:
        base = 100

    score = base
    modifiers.append(
        f"base={base} from temp={effective_temp:.1f}°C"
    )

    # Dewpoint — medical danger threshold
    if temp_dewpoint_c and temp_dewpoint_c > 26:
        score += 15
        modifiers.append(
            f"dewpoint={temp_dewpoint_c}°C > 26°C "
            f"→ medically_dangerous → +15"
        )

    # Duration
    if consecutive_days > 7:
        score += 25
        modifiers.append(
            f"heatwave_duration={consecutive_days}days → +25"
        )
    elif consecutive_days > 3:
        score += 15
        modifiers.append(
            f"heatwave_duration={consecutive_days}days → +15"
        )

    # Night temperature
    if night_temp_min and night_temp_min > 30:
        score += 10
        modifiers.append(
            f"night_min={night_temp_min}°C > 30°C "
            f"→ no_recovery_period → +10"
        )

    # Humidity
    if humidity_pct and humidity_pct > 70:
        score += 12
        modifiers.append(
            f"humidity={humidity_pct}% → +12"
        )

    # Infrastructure failures
    if electricity_outage_hours and electricity_outage_hours > 12:
        score += 15
        modifiers.append(
            f"electricity_outage={electricity_outage_hours}h → +15"
        )

    if water_shortage:
        score += 20
        modifiers.append("water_shortage_confirmed → +20")

    return min(score, 100), modifiers


def score_heavy_rain_hazard(
    precip_24h_mm: float | None,
    precip_72h_mm: float | None,
    cape_jkg: float | None,
    precip_prob_pct: float | None,
    terrain_type: str,
    drainage_quality: str,
    soil_saturated: bool,
) -> tuple[int, list[str]]:
    """
    Returns (score 0-100, list of modifiers applied)
    """
    modifiers = []

    if precip_24h_mm is None:
        return 20, ["precip_24h_unknown → default 20"]

    # Base score from 24h accumulation
    if precip_24h_mm < 25:
        base = 10
    elif precip_24h_mm < 50:
        base = 25
    elif precip_24h_mm < 100:
        base = 45
    elif precip_24h_mm < 150:
        base = 65
    elif precip_24h_mm < 200:
        base = 80
    else:
        base = 95

    score = base
    modifiers.append(
        f"base={base} from precip_24h={precip_24h_mm:.1f}mm"
    )

    # CAPE
    if cape_jkg:
        if cape_jkg > 3500:
            score += 15
            modifiers.append(
                f"cape={cape_jkg:.0f}J/kg → violent_storms → +15"
            )
        elif cape_jkg > 2500:
            score += 8
            modifiers.append(
                f"cape={cape_jkg:.0f}J/kg → severe_storm → +8"
            )

    # 72h accumulation
    if precip_72h_mm and precip_72h_mm > 300:
        score += 12
        modifiers.append(
            f"precip_72h={precip_72h_mm:.1f}mm > 300mm → +12"
        )

    # Terrain
    if terrain_type == "mountain":
        score += 20
        modifiers.append(
            "mountain → flash_flood+landslide_risk → +20"
        )
    elif terrain_type == "urban":
        score += 15
        modifiers.append(
            "urban → drainage_overwhelmed → +15"
        )

    # Drainage quality
    drainage_scores = {
        "critical": 15,
        "very_high": 15,
        "high": 10,
        "moderate": 5,
        "low": 0,
        "very_low": 0,
    }
    drain_add = drainage_scores.get(drainage_quality, 5)
    if drain_add > 0:
        score += drain_add
        modifiers.append(
            f"drainage_quality={drainage_quality} → +{drain_add}"
        )

    # Soil saturation
    if soil_saturated:
        score += 15
        modifiers.append("soil_saturated → +15")

    return min(score, 100), modifiers
```

### 6.6 app/agent/scoring/composite_scorer.py

```python
# app/agent/scoring/composite_scorer.py
# ─────────────────────────────────────────────────────────────────
# Final composite score computation.
# Applies weights, terrain multiplier, and override rules.
# ─────────────────────────────────────────────────────────────────

from app.models.output_models import RiskLevel

# Dimension weights — must sum to 1.0
WEIGHTS = {
    "hazard_severity": 0.25,
    "exposure": 0.25,
    "vulnerability": 0.20,
    "escalation_risk": 0.15,
    "response_capacity": 0.15,
}

# Terrain multipliers
TERRAIN_MULTIPLIERS = {
    "mountain": 1.20,
    "highland": 1.10,
    "coastal": 1.15,
    "urban": 1.10,
    "riverine_plain": 1.10,
    "desert": 1.08,
    "agricultural_plain": 1.00,
    "unknown": 1.05,
}


def compute_composite_score(
    hazard_score: int,
    exposure_score: int,
    vulnerability_score: int,
    escalation_score: int,
    response_capacity_score: int,
    terrain_type: str,
    # Override triggers
    usgs_alert_level: str | None = None,
    tsunami_flag: bool = False,
    dam_failure_risk: bool = False,
    flood_status: str | None = None,
    magnitude: float | None = None,
    population: int | None = None,
) -> tuple[float, float, float, bool, str | None, RiskLevel]:
    """
    Computes the final composite risk score.

    Returns:
        (
            score_before_terrain,
            terrain_multiplier,
            final_score,
            override_applied,
            override_reason,
            risk_level
        )
    """
    # Weighted sum
    weighted_hazard = hazard_score * WEIGHTS["hazard_severity"]
    weighted_exposure = (
        exposure_score * WEIGHTS["exposure"]
    )
    weighted_vulnerability = (
        vulnerability_score * WEIGHTS["vulnerability"]
    )
    weighted_escalation = (
        escalation_score * WEIGHTS["escalation_risk"]
    )
    weighted_response = (
        response_capacity_score * WEIGHTS["response_capacity"]
    )

    score_before_terrain = (
        weighted_hazard +
        weighted_exposure +
        weighted_vulnerability +
        weighted_escalation +
        weighted_response
    )

    # Apply terrain multiplier
    multiplier = TERRAIN_MULTIPLIERS.get(terrain_type, 1.05)
    final_score = min(score_before_terrain * multiplier, 100.0)

    # Check override conditions
    override_applied = False
    override_reason = None
    min_score = None

    if usgs_alert_level == "red" or tsunami_flag:
        min_score = 75.0
        override_reason = (
            "USGS PAGER red alert or tsunami flag — "
            "minimum EXTREME override applied"
        )
    elif dam_failure_risk and magnitude and magnitude >= 5.0:
        min_score = 75.0
        override_reason = (
            "Dam within impact zone with M5.0+ earthquake — "
            "minimum EXTREME override applied"
        )
    elif flood_status == "emergency":
        min_score = 50.0
        override_reason = (
            "Google Flood Hub status=emergency — "
            "minimum HIGH override applied"
        )
    elif magnitude and magnitude >= 7.0:
        min_score = 75.0
        override_reason = (
            f"Magnitude {magnitude} >= 7.0 — "
            "minimum EXTREME override applied"
        )
    elif population and population > 1_000_000:
        min_score = 50.0
        override_reason = (
            "Population > 1 million in impact zone — "
            "minimum HIGH override applied"
        )

    if min_score and final_score < min_score:
        final_score = min_score
        override_applied = True

    # Assign risk level
    if final_score < 25:
        risk_level = RiskLevel.LOW
    elif final_score < 50:
        risk_level = RiskLevel.MEDIUM
    elif final_score < 75:
        risk_level = RiskLevel.HIGH
    else:
        risk_level = RiskLevel.EXTREME

    return (
        round(score_before_terrain, 2),
        multiplier,
        round(final_score, 2),
        override_applied,
        override_reason,
        risk_level,
    )
```

---

## PART 7: SYSTEM PROMPT

### 7.1 app/agent/system_prompt.py

```python
# app/agent/system_prompt.py
# ─────────────────────────────────────────────────────────────────
# Complete system prompt for the Risk Analysis Agent.
# This is the core instruction set that drives all agent behavior.
# ─────────────────────────────────────────────────────────────────

RISK_ANALYSIS_SYSTEM_PROMPT = """
You are the Risk Analysis Agent for ClimaSync.ai — Pakistan's
AI-powered disaster management platform.

Your risk assessment directly determines whether evacuations
are ordered, which NGOs are deployed, and how many resources
are mobilized. Errors cost lives. Be accurate, thorough,
and always honest about uncertainty.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY EXECUTION SEQUENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Follow this exact sequence. Never skip. Never reorder.

STEP 1 → call get_location_data(district, province, location_id)
STEP 2 → call get_infrastructure_at_risk(lon, lat, disaster_kind)
STEP 3 → call get_current_disaster_data(disaster_kind, identifiers)
STEP 4 → call web_search: TERRAIN AND GEOGRAPHY
          Query: "[district] [province] Pakistan geography terrain
                 elevation landscape mountains plains desert"
STEP 5 → call web_search: DEMOGRAPHICS AND POVERTY
          Query: "[district] Pakistan poverty rate population
                 census 2023 literacy rate"
STEP 6 → call web_search: HISTORICAL DISASTER CONTEXT
          Query: "[district] Pakistan [disaster_kind] history
                 damage deaths displaced NDMA PDMA reliefweb.int"
STEP 7 → call web_search: CURRENT GROUND SITUATION
          Query: "[district] [province] Pakistan [disaster_kind]
                 2025 news damage casualties roads blocked"
STEP 8 → call disaster-type specific web searches (see below)
STEP 9 → compute all five dimension scores
STEP 10 → compute composite score and apply overrides
STEP 11 → produce complete RiskAssessmentReport JSON

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DISASTER-TYPE SPECIFIC WEB SEARCHES (STEP 8)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FOR FLOOD/FLASH_FLOOD:
  Search A: "[river_name] Pakistan dam release discharge 2025
             WAPDA barrage upstream level current"
  Search B: "[district] Sindh Punjab waterlogging soil
             saturation drainage 2025 monsoon"
  Search C: "[district] Pakistan agriculture crop harvest
             calendar [current_month]"
  Search D: "Pakistan NGO [district] flood relief operations
             2025 Alkhidmat Edhi Red Crescent"

FOR EARTHQUAKE:
  Search A: "[district] Pakistan fault line seismic zone
             Chaman Makran Himalayan active fault history"
  Search B: "[district] Pakistan building construction
             kutcha semi-pucca housing percentage rural"
  Search C: "aftershock probability M[magnitude] Pakistan
             [fault_name] sequence"
  Search D: "[district] Pakistan landslide history rockfall
             earthquake triggered road closure"

FOR HEATWAVE:
  Search A: "[district] Pakistan water supply access
             drinking water piped percentage shortage"
  Search B: "[district] Pakistan electricity load shedding
             hours summer 2025 power outage"
  Search C: "[province] Pakistan heatwave deaths casualties
             hospital history 2015 2022 2024"
  Search D: "[district] Pakistan outdoor workers agriculture
             labor construction workforce"

FOR HEAVY_RAIN/CYCLONE:
  Search A: "[district] Pakistan drainage system capacity
             storm drain urban flooding"
  Search B: "[district] Pakistan soil saturation waterlogging
             current monsoon 2025"
  Search C: "[district] Pakistan road condition flooding
             national highway provincial road closure"
  Search D: "Pakistan [district] cyclone storm history
             wind damage casualties"

FOR COLD_WAVE:
  Search A: "[district] Pakistan snowfall road closure
             mountain pass blocked winter"
  Search B: "[district] Pakistan heating fuel wood access
             winter cold wave vulnerable population"

FOR DUST_STORM:
  Search A: "[district] Pakistan dust storm history
             visibility road accident"
  Search B: "[district] Pakistan crop damage dust storm
             agriculture loss"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TERRAIN DETERMINATION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IF web search confirms terrain → use that
ELSE derive from database fields:
  elevation_m > 2000 + (province = gilgit_baltistan
    or azad_kashmir or khyber_pakhtunkhwa) → MOUNTAIN
  elevation_m 500-2000 + KPK/Balochistan → HIGHLAND
  elevation_m < 200 + (flood_risk_zone = zone_4 or zone_5)
    + Punjab/Sindh → RIVERINE_PLAIN
  elevation_m < 100 + Sindh + near coast → COASTAL
  population_density > 5000/km² → URBAN (override others)
  Balochistan interior low elevation → DESERT
  Punjab/Sindh flat moderate flood zone → AGRICULTURAL_PLAIN

Terrain multipliers for final score:
  MOUNTAIN: ×1.20    HIGHLAND: ×1.10
  COASTAL: ×1.15     URBAN: ×1.10
  RIVERINE_PLAIN: ×1.10   DESERT: ×1.08
  AGRICULTURAL_PLAIN: ×1.00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIVE DIMENSION SCORING RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WEIGHTS: Hazard=25%, Exposure=25%, Vulnerability=20%,
         Escalation=15%, Response_Capacity=15%

DIMENSION 1 — HAZARD SEVERITY (0-100):
Apply rules from hazard_scorer.py for your disaster type.
Show: base_score, each modifier, final score calculation.

DIMENSION 2 — EXPOSURE (0-100):
  Population score:
    <50k→10, 50-100k→25, 100-300k→40, 300-600k→60,
    600k-1M→75, 1-3M→88, >3M→100
    +15 if density>10,000/km², +10 if 5-10k, +5 if 1-5k
  
  Infrastructure score:
    0 hospitals→100, 1-2→70, 3-5→45, 6-10→25, >10→10
    +25 per critical dam/barrage, +15 per critical hospital,
    +10 per critical bridge
  
  EXPOSURE = (population_score × 0.55) +
             (infrastructure_score × 0.45)

DIMENSION 3 — VULNERABILITY (0-100):
  Building score:
    kutcha→95, semi_pucca→60, pucca→25
    mixed→weighted average (use Pakistan defaults if unknown)
  Drainage score:
    very_low→10, low→25, moderate→45, high→65,
    very_high→85, critical→100
  Infrastructure quality score: same scale as drainage
  Poverty score:
    <20%→20, 20-35%→40, 35-50%→60, >50%→80
    (use Pakistan provincial defaults if web search fails)
  Terrain vulnerability score:
    mountain→80, coastal→75, riverine→70, desert→65,
    urban→45, highland→60, plain→35
  
  VULNERABILITY = (building×0.30) + (drainage×0.20) +
                  (infra_quality×0.20) + (poverty×0.20) +
                  (terrain_vuln×0.10)

DIMENSION 4 — ESCALATION RISK (0-100):
  Trajectory score:
    rapidly_rising/active worsening→90
    rising/developing→65
    stable/holding→30
    improving/falling→10
  
  Secondary disaster score:
    earthquake→landslide (mountain + M5.5+) → +20
    earthquake→dam failure (dam<50km) → +30
    flood→disease (standing water >48h likely) → +15
    heatwave→grid failure (outage known) → +20
    heavy rain→flood (soil saturated + zone_4/5) → +25
  
  ESCALATION = (trajectory×0.60) + (secondary×0.40)

DIMENSION 5 — RESPONSE CAPACITY (0-100):
  Higher score = LOWER capacity = MORE vulnerable
  
  Medical:
    beds/1000: >2→15, 1-2→35, 0.5-1→60, 0.2-0.5→80, <0.2→95
    Pakistan average: 0.6/1000. Rural: 0.1-0.2/1000.
  Evacuation:
    capacity/population: >20%→10, 10-20%→30, 5-10%→55,
    2-5%→75, <2%→95
  Road access:
    national_highways_open→10, provincial_passable→30,
    district_roads_only→55, village_tracks_only→75,
    roads_blocked→95
  NGO presence:
    multiple_active→10, one_present→35, nearby_only→60,
    none_known→85
  
  RESPONSE = (medical×0.30) + (evacuation×0.25) +
             (road×0.25) + (ngo×0.20)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY OVERRIDE RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After computing composite:
  IF usgs_alert_level = red → minimum score 75 (EXTREME)
  IF tsunami_flag = TRUE → minimum score 75 (EXTREME)
  IF dam_failure_risk + M5.0+ → minimum score 75 (EXTREME)
  IF flood_status = emergency → minimum score 50 (HIGH)
  IF magnitude >= 7.0 → minimum score 75 (EXTREME)
  IF population > 1M + any breach → minimum score 50 (HIGH)

RISK LEVELS: 0-24=LOW, 25-49=MEDIUM, 50-74=HIGH, 75-100=EXTREME

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAKISTAN KNOWLEDGE BASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BUILDING VULNERABILITY BY REGION:
  Rural Sindh: 60-70% kutcha/semi-pucca
  Rural Punjab: 40-50% kutcha/semi-pucca
  Rural KPK/Balochistan: 70-80% kutcha
  Urban Karachi formal: 30% kutcha (informal settlements)
  Urban Lahore: 20% kutcha
  Kutcha collapses: M5.0+, dissolves in 72h flooding

DRAINAGE LIMITS:
  Karachi city drainage: 25mm/hour maximum design
  Lahore: 35mm/hour
  Rural Sindh: no formal drainage, all surface runoff
  Punjab canal areas: irrigation canals can overflow

HEALTHCARE:
  Pakistan national: 0.6 beds/1,000 population
  Rural areas: 0.1-0.2 beds/1,000
  DHQ hospital: serves entire district (300k-2M people)

ROAD NETWORK:
  National Highways (M-1,M-2,N-5): rarely close
  Provincial roads: close at >50mm rain/24h
  District roads: close at 30cm flood depth
  KPK mountain tracks: close at M5.5+ or heavy snow

POVERTY DEFAULTS (use if web search fails):
  Interior Sindh: 65%, Rural Balochistan: 65%
  Rural Punjab: 35%, Rural KPK: 45%
  Urban Karachi formal: 25%, Urban informal: 55%
  Mark all defaults with uncertainty flag

RIVER SYSTEM CONTEXT:
  Indus: Tarbela controls. Peak Aug-Sep.
  Jhelum: Mangla controls. Fast rise in Kashmir rain.
  Chenab: Indian releases + local rain compound.
  Ravi/Sutlej: Indian floodwater, politically sensitive.
  Kabul: Rapid rise, mountainous catchment.
  Downstream timing:
    Kashmir earthquake → Jhelum flood peak: 18-36 hours
    KPK heavy rain → Indus at Sukkur: 5-7 days

SEASONAL CONTEXT:
  July-September: Peak monsoon. Maximum flood risk.
  April-June: Heatwave season. Interior Sindh critical.
  October-November: Harvest. Crop loss amplifies damage.
  December-February: Cold waves. GB/KPK mountains.
  Ramadan context: daytime fasting amplifies heat risk.

FAULT SYSTEMS:
  Chaman Fault (Balochistan): M7.5+ potential
  Makran Subduction (Coastal Balochistan): Tsunami risk
  Himalayan Frontal Thrust (Punjab/KPK foothills): M8.0+
  Quetta Fault: directly under Quetta city

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UNCERTAINTY RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Never fabricate a number.
2. State uncertainty explicitly in justification.
3. Use Pakistan-context defaults where appropriate.
4. Document every default in assumptions_made list.
5. Add every gap to data_gaps list.
6. data_confidence:
   All data available → HIGH
   1-2 gaps with estimates → MEDIUM
   3+ gaps or major gaps → LOW

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Produce valid RiskAssessmentReport JSON.
Every score must have justification with cited data.
critical_actions_needed: minimum 5 items, urgency ordered.
time_sensitive_actions: actions needed within 6 hours only.
data_gaps: populate even if empty list [].
assumptions_made: every assumption explicitly listed.
web_search_findings: cite source URLs where available.
"""
```

---

## PART 8: AGENT DEFINITION

### 8.1 app/agent/risk_agent.py

```python
# app/agent/risk_agent.py
# ─────────────────────────────────────────────────────────────────
# Risk Analysis Agent definition using OpenAI Agents SDK.
# Wires together system prompt, tools, and output schema.
# ─────────────────────────────────────────────────────────────────

from agents import Agent
from agents.tool import WebSearchTool

from app.agent.system_prompt import RISK_ANALYSIS_SYSTEM_PROMPT
from app.agent.tools.location_tool import get_location_data
from app.agent.tools.infrastructure_tool import (
    get_infrastructure_at_risk
)
from app.agent.tools.disaster_data_tool import (
    get_current_disaster_data
)
from app.models.output_models import RiskAssessmentReport
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)


def create_risk_analysis_agent() -> Agent:
    """
    Creates and returns the Risk Analysis Agent instance.

    The agent uses GPT-4o for complex multi-step reasoning.
    It has four tools:
      1. get_location_data — reads collection DB location table
      2. get_infrastructure_at_risk — reads infrastructure table
      3. get_current_disaster_data — reads time-series tables
      4. WebSearchTool — built-in OpenAI web search

    Output is forced into RiskAssessmentReport schema via
    output_type parameter.
    """

    agent = Agent(
        name="ClimaSync Risk Analysis Agent",
        model=settings.openai_model,
        instructions=RISK_ANALYSIS_SYSTEM_PROMPT,
        tools=[
            get_location_data,
            get_infrastructure_at_risk,
            get_current_disaster_data,
            WebSearchTool(),
        ],
        output_type=RiskAssessmentReport,
    )

    logger.info(
        f"Risk Analysis Agent created. "
        f"Model: {settings.openai_model}"
    )

    return agent


# Module-level agent instance — created once at startup
risk_agent = create_risk_analysis_agent()
```

---

## PART 9: API ROUTES

### 9.1 app/api/routes/assessment_controller.py

```python
# app/api/routes/assessment_controller.py
# ─────────────────────────────────────────────────────────────────
# FastAPI route for triggering risk assessment.
# Receives breach payload from main system.
# Runs agent and returns structured report.
# ─────────────────────────────────────────────────────────────────

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from agents import Runner

from app.models.input_models import BreachPayload
from app.models.output_models import RiskAssessmentReport
from app.agent.risk_agent import risk_agent
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.exceptions import (
    http_agent_error,
    http_unauthorized,
)

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Assessment"])


def verify_api_key(x_api_key: str | None = None) -> None:
    """
    Validates internal API key from request header.
    All endpoints require this authentication.
    """
    from fastapi import Header
    if x_api_key != settings.internal_api_key:
        raise http_unauthorized()


@router.post(
    "/assess",
    response_model=RiskAssessmentReport,
    summary="Trigger Risk Analysis Assessment",
    description=(
        "Receives a verified disaster breach payload from the "
        "main ClimaSync system and runs the complete risk "
        "analysis agent pipeline. Returns structured "
        "RiskAssessmentReport."
    ),
)
async def trigger_assessment(
    payload: BreachPayload,
    x_api_key: str = Depends(
        lambda x_api_key: verify_api_key(x_api_key)
    ),
) -> RiskAssessmentReport:
    """
    Main endpoint for triggering risk analysis.

    Workflow:
    1. Validate incoming breach payload
    2. Build agent input message with full context
    3. Run agent with Runner.run()
    4. Extract structured RiskAssessmentReport from output
    5. Return to main system
    """

    assessment_id = str(uuid.uuid4())

    logger.info(
        f"Risk assessment triggered. "
        f"assessment_id={assessment_id} "
        f"breach_id={payload.breach_id} "
        f"disaster={payload.disaster_kind} "
        f"location={payload.district}, {payload.province}"
    )

    # Build comprehensive agent input message
    agent_input = _build_agent_input(payload, assessment_id)

    try:
        # Run the agent
        result = await Runner.run(
            risk_agent,
            input=agent_input,
            max_turns=settings.openai_max_turns,
        )

        # Extract the structured output
        report: RiskAssessmentReport = result.final_output

        logger.info(
            f"Assessment complete. "
            f"assessment_id={assessment_id} "
            f"risk_level={report.risk_level} "
            f"composite_score={report.composite_risk_score}"
        )

        return report

    except Exception as e:
        logger.error(
            f"Agent execution failed. "
            f"assessment_id={assessment_id} "
            f"error={str(e)}"
        )
        raise http_agent_error(str(e))


def _build_agent_input(
    payload: BreachPayload,
    assessment_id: str,
) -> str:
    """
    Builds the complete input message for the agent.
    Includes all breach context so agent has full information
    before calling any tools.
    """

    current_time = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    lines = [
        f"RISK ASSESSMENT REQUEST",
        f"Assessment ID: {assessment_id}",
        f"Current Time: {current_time}",
        f"",
        f"BREACH INFORMATION:",
        f"  breach_id: {payload.breach_id}",
        f"  disaster_kind: {payload.disaster_kind}",
        f"  breach_severity: {payload.breach_severity}",
        f"  metric_name: {payload.metric_name}",
        f"  observed_value: {payload.observed_value}",
        f"  threshold_value: {payload.threshold_value}",
        f"  observation_time: {payload.observation_time}",
        f"  is_forecast_breach: {payload.is_forecast_breach}",
    ]

    if payload.forecast_horizon_h:
        lines.append(
            f"  forecast_horizon_h: {payload.forecast_horizon_h}"
        )

    lines += [
        f"",
        f"LOCATION INFORMATION:",
        f"  location_name: {payload.location_name}",
        f"  district: {payload.district}",
        f"  province: {payload.province}",
        f"  latitude: {payload.latitude}",
        f"  longitude: {payload.longitude}",
        f"  source_api: {payload.source_api}",
        f"",
        f"DATABASE IDENTIFIERS:",
        f"  gauge_id: {payload.gauge_id or 'N/A'}",
        f"  usgs_event_id: {payload.usgs_event_id or 'N/A'}",
        f"  weather_location_id: "
        f"{payload.weather_location_id or 'N/A'}",
        f"",
        f"INSTRUCTIONS:",
        f"Follow your mandatory 11-step workflow exactly.",
        f"Use assessment_id={assessment_id} in your output.",
        f"The disaster_kind is: {payload.disaster_kind}",
        f"Execute all disaster-type specific web searches",
        f"for {payload.disaster_kind} as defined.",
        f"Produce complete RiskAssessmentReport JSON.",
    ]

    return "\n".join(lines)
```

### 9.2 app/api/routes/health_controller.py

```python
# app/api/routes/health_controller.py
# ─────────────────────────────────────────────────────────────────
# Health check endpoint for monitoring and load balancers.
# Returns service status and database connectivity.
# ─────────────────────────────────────────────────────────────────

from datetime import datetime, timezone
from fastapi import APIRouter
from app.database.connection import get_pool
from app.core.config import settings

router = APIRouter(tags=["Health"])
_start_time = datetime.now(timezone.utc)


@router.get("/health")
async def health_check() -> dict:
    """
    Basic health check. Returns 200 if service is running.
    """
    uptime = (
        datetime.now(timezone.utc) - _start_time
    ).total_seconds()

    db_healthy = True
    db_error = None

    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
    except Exception as e:
        db_healthy = False
        db_error = str(e)

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": settings.service_name,
        "environment": settings.app_env,
        "uptime_seconds": round(uptime, 1),
        "database_connected": db_healthy,
        "database_error": db_error,
        "model": settings.openai_model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

---

## PART 10: APPLICATION ENTRY POINT

### 10.1 app/main.py

```python
# app/main.py
# ─────────────────────────────────────────────────────────────────
# FastAPI application entry point.
# Manages startup, shutdown, and route registration.
# ─────────────────────────────────────────────────────────────────

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
    FastAPI lifespan context manager.
    Handles startup and shutdown sequences.
    """
    # ── STARTUP ───────────────────────────────────────────────────
    logger.info(
        f"Starting {settings.service_name} on "
        f"port {settings.app_port}"
    )

    # Step 1: Connect to collection database
    await create_pool()
    logger.info("Collection database pool created")

    # Step 2: Log ready state
    logger.info(
        f"{settings.service_name} ready. "
        f"Environment: {settings.app_env}. "
        f"Model: {settings.openai_model}"
    )

    yield  # Application runs here

    # ── SHUTDOWN ──────────────────────────────────────────────────
    logger.info(f"Shutting down {settings.service_name}...")
    await close_pool()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="ClimaSync Risk Analysis Agent",
    description=(
        "AI-powered disaster risk analysis for Pakistan. "
        "Analyzes flood, earthquake, and weather disasters "
        "using multi-source data and web search."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router)
app.include_router(assess_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.app_env == "development",
    )
```

---

## PART 11: BUILD ORDER AND SUCCESS CRITERIA

### 11.1 Exact Build Order

```
Build in this exact sequence:

1.  pyproject.toml              ← Install dependencies first
2.  .env                        ← Set all environment variables
3.  app/core/config.py          ← All config reads from here
4.  app/core/logger.py          ← All logging through here
5.  app/core/exceptions.py      ← All error types defined
6.  app/database/connection.py  ← Database pool
7.  app/database/queries/       ← All SQL strings (3 files)
8.  app/models/input_models.py  ← Input validation
9.  app/models/output_models.py ← Output schema
10. app/agent/scoring/          ← All scoring functions (7 files)
11. app/agent/tools/location_tool.py
12. app/agent/tools/infrastructure_tool.py
13. app/agent/tools/disaster_data_tool.py
14. app/agent/tools/web_search_tool.py
15. app/agent/system_prompt.py  ← Complete system prompt
16. app/agent/risk_agent.py     ← Wire everything together
17. app/api/routes/health_controller.py
18. app/api/routes/assessment_controller.py
19. app/main.py                 ← Final entry point
20. tests/                      ← Test all components
```

### 11.2 Success Criteria

```
The Risk Analysis Agent is complete and working when:

✅ Service starts on port 8002 without errors
✅ GET /health returns {"status": "healthy"}
✅ Database pool connects to collection DB successfully
✅ Agent is created without errors at startup

✅ POST /api/v1/assess with earthquake payload:
   → get_location_data called with correct district/province
   → get_infrastructure_at_risk called with correct radius
   → get_current_disaster_data returns seismic_events data
   → Web search runs 8 queries (4 generic + 4 earthquake)
   → All five dimension scores computed with justifications
   → Composite score computed with terrain multiplier
   → Override rules applied if applicable
   → Valid RiskAssessmentReport JSON returned

✅ POST /api/v1/assess with flood payload:
   → flood_gauge_current data retrieved
   → flood_gauge_forecasts 24h/48h/72h retrieved
   → Upstream dam status web searched
   → Soil saturation web searched
   → Probabilistic forecast (p50/p90) used in escalation
   → River trend applied in hazard scoring

✅ POST /api/v1/assess with heatwave payload:
   → Weather hourly current data retrieved
   → 5-day daily summaries retrieved
   → Consecutive heatwave days computed
   → Dewpoint threshold checked
   → Electricity outage web searched
   → Water availability web searched

✅ All five dimension scores have justification strings
✅ data_gaps list populated (empty list if none)
✅ assumptions_made list populated
✅ critical_actions_needed has minimum 5 items
✅ web_search_findings cites sources
✅ Unauthorized request returns HTTP 403
✅ Invalid payload returns HTTP 422
✅ Agent failure returns HTTP 500 with detail
```

---

This document is complete. Every file, every function, every SQL query, every scoring rule, every configuration value, and every design decision is documented. Build in the sequence specified and verify against the success criteria checklist.