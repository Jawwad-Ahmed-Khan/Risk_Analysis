# app/database/queries/location_queries.py
# ─────────────────────────────────────────────────────────────────
# All SQL queries for reading pakistan_locations from the
# collection database.
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
        CASE location_tier::TEXT
            WHEN 'tier_1_provincial_capital' THEN 1
            WHEN 'tier_2_district_headquarters' THEN 2
            WHEN 'tier_3_tehsil_headquarters' THEN 3
            ELSE 4
        END
    LIMIT 1
"""

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
