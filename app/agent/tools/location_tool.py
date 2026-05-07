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
    table in the collection database. Returns population,
    vulnerability levels, risk zones, infrastructure quality,
    drainage quality, building stock, and elevation data for 
    the affected location. Call this first in every assessment.
    """
    pool = get_pool()

    try:
        async with pool.acquire() as conn:
            # 1. Determine query based on ID availability
            if location_id:
                row = await conn.fetchrow(GET_LOCATION_BY_ID, location_id)
            else:
                row = await conn.fetchrow(
                    GET_LOCATION_BY_DISTRICT,
                    district,
                    province
                )

            # 2. Handle missing data
            if not row:
                logger.warning(f"Location not found: {district}, {province}")
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

            # 3. Process and augment result
            result = dict(row)
            result["found"] = True

            # Add computed fields for agent convenience
            if result.get("population") and result.get("population_density"):
                result["population_note"] = (
                    f"Population: {result['population']:,} people "
                    f"at density {result['population_density']:.1f}/km²"
                )

            logger.info(f"Location data retrieved for {district}, {province}")
            return json.dumps(result, default=str)

    except Exception as e:
        logger.error(f"Location tool error: {e}")
        return json.dumps({
            "found": False,
            "error": str(e),
            "message": "Database error. Use web search for location data."
        })
