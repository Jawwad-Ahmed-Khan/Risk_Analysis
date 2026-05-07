# app/agent/tools/disaster_data_tool.py
# ─────────────────────────────────────────────────────────────────
# Tool 3: get_current_disaster_data
# Reads time-series disaster measurements and forecasts.
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
    Retrieves current disaster measurement data from the 
    collection database. For earthquake: reads seismic_events.
    For flood/flash_flood: reads flood_gauge_current and 
    flood_gauge_forecasts. For heatwave/heavy_rain/cyclone/
    cold_wave/dust_storm: reads weather_hourly_window and 
    weather_daily_summaries. Call this third in every 
    assessment.
    """
    pool = get_pool()

    try:
        async with pool.acquire() as conn:
            # ── EARTHQUAKE BRANCH ─────────────────────────────────
            if disaster_kind == "earthquake":
                event = await conn.fetchrow(GET_SEISMIC_EVENT_BY_USGS_ID, usgs_event_id)
                if not event:
                    return json.dumps({"found": False, "message": "Earthquake data not yet available in DB."})
                
                result = dict(event)
                result.pop("raw_api_response", None) # Remove bulky JSON
                
                if longitude and latitude:
                    nearby = await conn.fetch(GET_RECENT_EARTHQUAKES_NEAR_LOCATION, longitude, latitude, 100000)
                    result["recent_nearby_earthquakes"] = [dict(r) for r in nearby]
                
                return json.dumps(result, default=str)

            # ── FLOOD BRANCH ──────────────────────────────────────
            elif disaster_kind in ("flood", "flash_flood"):
                current = await conn.fetchrow(GET_FLOOD_GAUGE_CURRENT_BY_ID, gauge_id)
                forecasts = await conn.fetch(GET_FLOOD_FORECASTS_FOR_GAUGE, gauge_id)
                
                # Filter forecasts closest to 24h, 48h, 72h horizons
                f_list = [dict(f) for f in forecasts]
                def find_horizon(h):
                    return next((f for f in f_list if h-4 <= f["forecast_horizon_h"] <= h+4), None)

                result = {
                    "current_gauge": dict(current) if current else None,
                    "forecast_24h": find_horizon(24),
                    "forecast_48h": find_horizon(48),
                    "forecast_72h": find_horizon(72),
                }
                
                if result["current_gauge"]:
                    result["current_gauge"].pop("raw_api_response", None)
                
                if longitude and latitude:
                    nearby = await conn.fetch(GET_NEARBY_FLOOD_GAUGES, longitude, latitude, 100000)
                    result["nearby_gauges"] = [dict(r) for r in nearby]
                
                return json.dumps(result, default=str)

            # ── WEATHER BRANCH ────────────────────────────────────
            elif disaster_kind in ("heatwave", "heavy_rain", "cyclone", "cold_wave", "dust_storm", "landslide", "drought"):
                current = await conn.fetchrow(GET_CURRENT_WEATHER_FOR_LOCATION, weather_location_id)
                daily = await conn.fetch(GET_WEATHER_DAILY_SUMMARY_5DAY, weather_location_id)
                hourly = await conn.fetch(GET_HOURLY_FORECAST_NEXT_72H, weather_location_id)
                
                daily_list = [dict(d) for d in daily]
                hourly_list = [dict(h) for h in hourly]
                
                # Compute Insightful Metrics
                result = {
                    "current_weather": dict(current) if current else None,
                    "daily_summaries": daily_list,
                    "insights": {
                        "consecutive_heatwave_days": sum(1 for d in daily_list if d.get("flag_heatwave_day")),
                        "peak_temp_72h": max((h.get("temp_c") or 0 for h in hourly_list), default=0),
                        "peak_precip_24h_in_72h": max((h.get("precip_24h_mm") or 0 for h in hourly_list), default=0),
                        "peak_cape_jkg": max((h.get("cape_jkg") or 0 for h in hourly_list), default=0),
                        "peak_wind_gusts": max((h.get("wind_gusts_kmh") or 0 for h in hourly_list), default=0),
                    }
                }
                return json.dumps(result, default=str)

            else:
                return json.dumps({"error": f"Disaster type {disaster_kind} not supported by this tool."})

    except Exception as e:
        logger.error(f"Disaster data tool error: {e}")
        return json.dumps({"error": str(e), "message": "DB Error. Use web search to fill gaps."})
