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
    Represents the validated payload sent by the main ClimaSync system 
    when a disaster threshold breach is detected and a risk analysis 
    is requested.

    This model serves as the primary input for the Risk Analysis Agent, 
    containing the physical measurements of the breach, the location 
    context, and the necessary identifiers to fetch detailed 
    environmental and infrastructure data from the database.
    """
    breach_id: str = Field(..., description="UUID of the breach record in the main system")
    disaster_kind: DisasterKind = Field(..., description="The type of disaster being analyzed")
    location_name: str = Field(..., min_length=1, description="Friendly name of the location")
    district: str = Field(..., min_length=1, description="District name for database lookup")
    province: Province = Field(..., description="Province of the affected area")
    latitude: float = Field(..., ge=23.0, le=38.0, description="Latitude within Pakistan bounds")
    longitude: float = Field(..., ge=60.0, le=78.0, description="Longitude within Pakistan bounds")
    observed_value: float = Field(..., description="The measured value that caused the breach")
    threshold_value: float = Field(..., description="The threshold limit that was exceeded")
    breach_severity: BreachSeverity = Field(..., description="Pre-calculated severity of the breach")
    metric_name: str = Field(..., min_length=1, description="The specific metric name (e.g. gauge_pct_of_danger)")
    observation_time: str = Field(..., description="ISO 8601 timestamp of the observation")
    source_api: SourceAPI = Field(..., description="The API that provided the data")

    # Optional fields with defaults
    is_forecast_breach: bool = Field(default=False, description="Whether this is a predicted future breach")
    forecast_horizon_h: Optional[int] = Field(default=None, description="Hours into the future for predicted breaches")
    gauge_id: Optional[str] = Field(default=None, description="UUID for flood gauges in the registry")
    usgs_event_id: Optional[str] = Field(default=None, description="Unique USGS event ID for earthquakes")
    weather_location_id: Optional[str] = Field(default=None, description="UUID for weather locations")

    @field_validator("forecast_horizon_h")
    @classmethod
    def validate_forecast_horizon(cls, v, info):
        """
        Ensures forecast_horizon_h is present if is_forecast_breach is True.
        """
        if info.data.get("is_forecast_breach") and v is None:
            raise ValueError(
                "forecast_horizon_h is required when is_forecast_breach is set to True"
            )
        return v
