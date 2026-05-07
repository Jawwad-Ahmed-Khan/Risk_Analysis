# app/database/queries/disaster_data_queries.py
# ─────────────────────────────────────────────────────────────────
# SQL queries for reading time-series disaster data.
# Covers earthquake, flood gauge, and weather data.
# ─────────────────────────────────────────────────────────────────

GET_SEISMIC_EVENT_BY_USGS_ID = """
    SELECT
        event_id,
        usgs_event_id,
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

GET_FLOOD_GAUGE_CURRENT_BY_ID = """
    SELECT
        fc.*,
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

GET_CURRENT_WEATHER_FOR_LOCATION = """
    SELECT
        location_id,
        location_name,
        district,
        province,
        forecast_for_datetime,
        temp_c,
        temp_apparent_c,
        temp_dewpoint_c,
        precip_mm,
        precip_prob_pct,
        precip_3h_mm,
        precip_6h_mm,
        precip_12h_mm,
        precip_24h_mm,
        precip_72h_mm,
        wind_speed_kmh,
        wind_gusts_kmh,
        humidity_pct,
        pressure_hpa,
        uv_index,
        cape_jkg,
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
        breach_observed_value
    FROM weather_hourly_window
    WHERE location_id = $1
      AND day_offset = 0
      AND forecast_for_datetime <= now()
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
        precip_prob_max_pct,
        wind_speed_max_kmh,
        dominant_condition,
        uv_index_max,
        flag_extreme_heat_day,
        flag_heatwave_day,
        flag_heavy_rain_day,
        flag_storm_day,
        flag_cold_wave_day,
        worst_breach_severity
    FROM weather_daily_summaries
    WHERE location_id = $1
    ORDER BY day_offset ASC
"""

GET_HOURLY_FORECAST_NEXT_72H = """
    SELECT
        forecast_for_datetime,
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
