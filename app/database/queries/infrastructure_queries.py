# app/database/queries/infrastructure_queries.py
# ─────────────────────────────────────────────────────────────────
# SQL queries for reading pakistan_infrastructure table.
# Returns critical assets within impact radius of disaster.
# ─────────────────────────────────────────────────────────────────

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

GET_HOSPITALS_WITHIN_RADIUS = """
    SELECT
        asset_id,
        asset_name,
        asset_type,
        capacity AS beds,
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
        distance_km ASC
"""

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

GET_EVACUATION_CENTERS_WITHIN_RADIUS = """
    SELECT
        asset_id,
        asset_name,
        asset_type,
        capacity AS shelter_capacity,
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
