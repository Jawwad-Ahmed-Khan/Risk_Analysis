# app/agent/scoring/hazard_scorer.py
# ─────────────────────────────────────────────────────────────────
# Deterministic hazard severity scoring for all disaster types.
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
    dam_within_50km: bool
) -> tuple[int, list[str]]:
    modifiers = []

    # Base score from magnitude
    if magnitude < 4.0: base = 10
    elif magnitude < 5.0: base = 25
    elif magnitude < 6.0: base = 50
    elif magnitude < 7.0: base = 75
    elif magnitude < 8.0: base = 90
    else: base = 100

    score = base
    modifiers.append(f"base_score={base} from M{magnitude}")

    if depth_km is not None:
        if depth_km < 70:
            score += 20
            modifiers.append("shallow_depth(<70km) → +20")
        elif depth_km <= 300:
            score += 8
            modifiers.append("intermediate_depth(70-300km) → +8")

    if magnitude_was_revised and initial_magnitude:
        if magnitude > initial_magnitude:
            score += 10
            modifiers.append("magnitude_revised_UP → +10")
        else:
            score -= 5
            modifiers.append("magnitude_revised_DOWN → -5")

    if usgs_alert_level == "red":
        score = max(score, 90)
        modifiers.append("usgs_alert_red → min 90")
    elif usgs_alert_level == "orange":
        score = max(score, 70)
        modifiers.append("usgs_alert_orange → min 70")

    if significance and significance > 800:
        score += 10
        modifiers.append("significance > 800 → +10")

    if felt_reports and felt_reports > 1000:
        score += 5
        modifiers.append("felt_reports > 1000 → +5")

    if tsunami_flag:
        score += 25
        modifiers.append("tsunami_flag → +25")

    if terrain_type == "MOUNTAIN" and magnitude >= 5.5:
        score += 15
        modifiers.append("mountain_terrain + M5.5+ → +15")

    if dam_within_50km and magnitude >= 5.0:
        score += 20
        modifiers.append("dam_within_50km + M5.0+ → +20")

    return min(score, 100), modifiers


def score_flood_hazard(
    pct_of_danger: float | None,
    river_trend: str,
    hours_to_danger: float | None,
    forecast_72h_danger_prob: float | None,
    upstream_area_sqkm: float | None,
    pct_of_historical_max: float | None,
    terrain_type: str,
    soil_saturated: bool
) -> tuple[int, list[str]]:
    modifiers = []
    if pct_of_danger is None:
        return 10, ["pct_of_danger_missing"]

    if pct_of_danger < 50: base = 10
    elif pct_of_danger < 70: base = 25
    elif pct_of_danger < 85: base = 45
    elif pct_of_danger < 100: base = 65
    elif pct_of_danger < 120: base = 80
    else: base = 95

    score = base
    modifiers.append(f"base={base} from pct_of_danger={pct_of_danger}")

    trends = {"rapidly_rising": 20, "rising": 10, "stable": 0, "falling": -10, "rapidly_falling": -15}
    trend_mod = trends.get(river_trend, 0)
    score += trend_mod
    if trend_mod != 0:
        modifiers.append(f"{river_trend} → {trend_mod}")

    if hours_to_danger is not None:
        if hours_to_danger < 6:
            score += 15
            modifiers.append("hours_to_danger<6 → +15")
        elif hours_to_danger <= 12:
            score += 8
            modifiers.append("hours_to_danger 6-12 → +8")

    if forecast_72h_danger_prob is not None:
        if forecast_72h_danger_prob > 70:
            score += 15
            modifiers.append("72h_prob>70% → +15")
        elif forecast_72h_danger_prob >= 40:
            score += 8
            modifiers.append("72h_prob 40-70% → +8")

    if upstream_area_sqkm:
        if upstream_area_sqkm > 200000:
            score += 12
            modifiers.append("upstream>200k km² → +12")
        elif upstream_area_sqkm > 100000:
            score += 8
            modifiers.append("upstream>100k km² → +8")

    if pct_of_historical_max and pct_of_historical_max > 90:
        score += 15
        modifiers.append("pct_historical_max>90% → +15")

    if terrain_type == "MOUNTAIN":
        score += 15
        modifiers.append("mountain_terrain → +15")

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
    water_shortage: bool
) -> tuple[int, list[str]]:
    modifiers = []
    if temp_max_c is None:
        return 5, ["temp_missing"]

    effective_temp = max(temp_max_c, temp_apparent_c or 0)
    if temp_apparent_c and temp_apparent_c > temp_max_c:
        modifiers.append(f"using_apparent_temp={temp_apparent_c}")

    if effective_temp < 40: base = 5
    elif effective_temp <= 43: base = 25
    elif effective_temp <= 46: base = 50
    elif effective_temp <= 49: base = 70
    elif effective_temp <= 52: base = 85
    else: base = 100

    score = base
    modifiers.append(f"base={base} from temp={effective_temp}")

    if temp_dewpoint_c and temp_dewpoint_c > 26:
        score += 15
        modifiers.append("dewpoint>26°C → +15")

    if consecutive_days > 7:
        score += 25
        modifiers.append("duration>7days → +25")
    elif consecutive_days > 3:
        score += 15
        modifiers.append("duration>3days → +15")

    if night_temp_min and night_temp_min > 30:
        score += 10
        modifiers.append("night_min>30°C → +10")

    if humidity_pct and humidity_pct > 70:
        score += 12
        modifiers.append("humidity>70% → +12")

    if electricity_outage_hours and electricity_outage_hours > 12:
        score += 15
        modifiers.append("electricity_outage>12h → +15")

    if water_shortage:
        score += 20
        modifiers.append("water_shortage → +20")

    return min(score, 100), modifiers


def score_heavy_rain_hazard(
    precip_24h_mm: float | None,
    precip_72h_mm: float | None,
    cape_jkg: float | None,
    precip_prob_pct: float | None,
    terrain_type: str,
    drainage_quality: str,
    soil_saturated: bool
) -> tuple[int, list[str]]:
    modifiers = []
    if precip_24h_mm is None:
        return 10, ["precip_missing"]

    if precip_24h_mm < 25: base = 10
    elif precip_24h_mm < 50: base = 25
    elif precip_24h_mm < 100: base = 45
    elif precip_24h_mm < 150: base = 65
    elif precip_24h_mm < 200: base = 80
    else: base = 95

    score = base
    modifiers.append(f"base={base} from precip_24h={precip_24h_mm}")

    if cape_jkg:
        if cape_jkg > 3500:
            score += 15
            modifiers.append("cape>3500 → +15")
        elif cape_jkg > 2500:
            score += 8
            modifiers.append("cape > 2500 → +8")

    if precip_72h_mm and precip_72h_mm > 300:
        score += 12
        modifiers.append("precip_72h>300 → +12")

    if terrain_type == "MOUNTAIN":
        score += 20
        modifiers.append("mountain → +20")
    elif terrain_type == "URBAN":
        score += 15
        modifiers.append("urban → +15")

    if drainage_quality in ("very_high", "critical"):
        score += 15
        modifiers.append(f"drainage_{drainage_quality} → +15")
    elif drainage_quality == "high":
        score += 10
        modifiers.append("drainage_high → +10")
    elif drainage_quality == "moderate":
        score += 5
        modifiers.append("drainage_moderate → +5")

    if soil_saturated:
        score += 15
        modifiers.append("soil_saturated → +15")

    return min(score, 100), modifiers
