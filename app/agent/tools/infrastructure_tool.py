# app/agent/tools/infrastructure_tool.py
# ─────────────────────────────────────────────────────────────────
# Tool 2: get_infrastructure_at_risk
# Finds all critical infrastructure within disaster impact radius.
# ─────────────────────────────────────────────────────────────────

import asyncio
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

# Impact radius configuration by disaster type and magnitude
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
    "heatwave": 50,
    "heavy_rain": 20,
    "cyclone": 80,
    "cold_wave": 50,
    "dust_storm": 30,
    "landslide": 15,
    "drought": 100,
}


def get_radius_meters(disaster_kind: str, magnitude: float | None = None) -> float:
    """
    Returns impact radius in meters (km * 1000).
    For earthquake: uses magnitude-specific ranges.
    For others: uses disaster_kind key directly.
    """
    if disaster_kind == "earthquake":
        if magnitude is not None:
            if magnitude < 5.0:
                km = IMPACT_RADIUS_KM["earthquake"]["M4-5"]
            elif magnitude < 6.0:
                km = IMPACT_RADIUS_KM["earthquake"]["M5-6"]
            elif magnitude < 7.0:
                km = IMPACT_RADIUS_KM["earthquake"]["M6-7"]
            else:
                km = IMPACT_RADIUS_KM["earthquake"]["M7+"]
        else:
            km = IMPACT_RADIUS_KM["earthquake"]["default"]
    else:
        km = IMPACT_RADIUS_KM.get(disaster_kind, 25)

    return float(km * 1000)


@function_tool
async def get_infrastructure_at_risk(
    longitude: float,
    latitude: float,
    disaster_kind: str,
    magnitude: float | None = None,
) -> str:
    """
    Finds all critical infrastructure assets within the impact
    radius of the disaster location. Returns hospitals, schools,
    bridges, dams, barrages, and evacuation centers with their
    capacity and vulnerability. Call this second in every 
    assessment after get_location_data.
    """
    pool = get_pool()
    radius_m = get_radius_meters(disaster_kind, magnitude)

    try:
        async with pool.acquire() as conn:
            # Execute DB queries sequentially on the acquired connection
            # Note: asyncpg connections do not support concurrent operations
            infra_rows = await conn.fetch(GET_INFRASTRUCTURE_WITHIN_RADIUS, longitude, latitude, radius_m)
            hosp_rows = await conn.fetch(GET_HOSPITALS_WITHIN_RADIUS, longitude, latitude, radius_m)
            dam_rows = await conn.fetch(GET_DAMS_WITHIN_RADIUS, longitude, latitude, radius_m)
            evac_rows = await conn.fetch(GET_EVACUATION_CENTERS_WITHIN_RADIUS, longitude, latitude, radius_m)

        # Categorize results by asset_type
        all_assets = [dict(r) for r in infra_rows]
        hospitals = [dict(r) for r in hosp_rows]
        dams_and_barrages = [dict(r) for r in dam_rows]
        evacuation_centers = [dict(r) for r in evac_rows]

        # Compute totals and critical metrics
        total_hospital_beds = sum(h.get("beds") or 0 for h in hospitals)
        
        schools = [a for a in all_assets if a.get("asset_type") == "school"]
        total_school_students = sum(s.get("serves_population") or 0 for s in schools)
        
        total_evacuation_capacity = sum(e.get("shelter_capacity") or 0 for e in evacuation_centers)
        
        critical_asset_names = [a.get("asset_name") for a in all_assets if a.get("is_critical")]

        result = {
            "impact_radius_km": radius_m / 1000,
            "total_assets_found": len(all_assets),
            "critical_assets_count": len(critical_asset_names),
            "critical_asset_names": critical_asset_names,
            "total_hospital_beds": total_hospital_beds,
            "total_school_students": total_school_students,
            "total_evacuation_capacity": total_evacuation_capacity,
            "categories": {
                "hospitals": hospitals,
                "dams_and_barrages": dams_and_barrages,
                "evacuation_centers": evacuation_centers,
                "schools": schools,
                "bridges": [a for a in all_assets if a.get("asset_type") == "bridge"]
            }
        }

        logger.info(f"Infrastructure analysis complete for radius {radius_m/1000}km")
        return json.dumps(result, default=str)

    except Exception as e:
        logger.error(f"Infrastructure tool error: {e}")
        return json.dumps({
            "error": str(e),
            "message": "Error retrieving infrastructure. Handle as a data gap."
        })
