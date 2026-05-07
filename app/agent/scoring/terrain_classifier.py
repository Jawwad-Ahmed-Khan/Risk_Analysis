# app/agent/scoring/terrain_classifier.py
# ─────────────────────────────────────────────────────────────────
# Logic for determining terrain type and associated risk multiplier.
# ─────────────────────────────────────────────────────────────────

def classify_terrain(
    elevation_m: float,
    province: str,
    flood_risk_zone: str,
    population_density: float,
    web_search_result: str = None
) -> tuple[str, str, float]:
    """
    Classifies the terrain type based on geography, database metrics,
    and optional web search findings.

    Returns: (terrain_type, source, multiplier)
    """
    multipliers = {
        "MOUNTAIN": 1.20,
        "HIGHLAND": 1.10,
        "COASTAL": 1.15,
        "URBAN": 1.10,
        "RIVERINE_PLAIN": 1.10,
        "DESERT": 1.08,
        "AGRICULTURAL_PLAIN": 1.00,
        "unknown": 1.05
    }

    # 1. Web Search Override
    if web_search_result:
        terrain_type = web_search_result.upper()
        if terrain_type in multipliers:
            return terrain_type, "web_search", multipliers[terrain_type]

    # 2. Urban Density Priority
    if population_density > 5000:
        return "URBAN", "database_derived", multipliers["URBAN"]

    # 3. Mountain
    if elevation_m > 2000 and province in ("gilgit_baltistan", "azad_kashmir", "khyber_pakhtunkhwa"):
        return "MOUNTAIN", "database_derived", multipliers["MOUNTAIN"]

    # 4. Highland
    if 500 <= elevation_m <= 2000 and province in ("khyber_pakhtunkhwa", "balochistan"):
        return "HIGHLAND", "database_derived", multipliers["HIGHLAND"]

    # 5. Riverine Plain
    if elevation_m < 200 and flood_risk_zone in ("zone_4_very_high", "zone_5_critical") and province in ("punjab", "sindh"):
        return "RIVERINE_PLAIN", "database_derived", multipliers["RIVERINE_PLAIN"]

    # 6. Coastal
    if province == "sindh" and elevation_m < 100:
        # Note: Ideally checked with a distance to coast query, but Sindh + low elev is a good proxy for risk modeling
        return "COASTAL", "database_derived", multipliers["COASTAL"]

    # 7. Desert
    if province == "balochistan" and elevation_m < 500:
        return "DESERT", "database_derived", multipliers["DESERT"]

    # 8. Default
    return "AGRICULTURAL_PLAIN", "database_derived", multipliers["AGRICULTURAL_PLAIN"]
