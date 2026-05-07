# app/agent/scoring/escalation_scorer.py
# ─────────────────────────────────────────────────────────────────
# Logic for assessing the trajectory and cascading risk.
# ─────────────────────────────────────────────────────────────────

def score_escalation(
    river_trend: str = None,
    is_situation_worsening: bool = False,
    secondary_disasters: list[str] = None,
    forecast_72h_extreme_prob: float = None,
    hours_to_peak: float = None,
    soil_saturated: bool = False,
    dam_failure_risk: bool = False,
    terrain_type: str = "unknown",
    magnitude: float = None,
    flood_status: str = None
) -> tuple[int, int, int, list[str]]:
    """
    Returns: (escalation_score, trajectory_score, secondary_score, secondary_list)
    """
    # 1. Trajectory Score
    if river_trend in ("rapidly_rising",) or is_situation_worsening:
        traj_score = 90
    elif river_trend in ("rising",) or flood_status == "warning":
        traj_score = 65
    elif river_trend == "stable":
        traj_score = 30
    elif river_trend in ("falling", "rapidly_falling"):
        traj_score = 10
    else:
        traj_score = 40 # Default unknown

    # 2. Secondary Disaster Score
    secondary_score = 0
    secondary_list = []

    # Earthquake triggers
    if magnitude and magnitude >= 5.5 and terrain_type == "MOUNTAIN":
        secondary_score += 20
        secondary_list.append("landslide_risk")
    
    if magnitude and magnitude >= 5.0 and dam_failure_risk:
        secondary_score += 30
        secondary_list.append("dam_failure")

    # Flood triggers
    # We assume 'secondary_disasters' might contain keywords like 'standing_water'
    if (flood_status == "emergency" or (river_trend == "stable" and terrain_type == "RIVERINE_PLAIN")):
        secondary_score += 15
        secondary_list.append("disease_outbreak")

    # Heatwave triggers
    # Handled via explicit flags in agent context, here we check for secondary_disasters list
    if secondary_disasters and "grid_failure" in secondary_disasters:
        secondary_score += 20
        secondary_list.append("grid_failure")

    # Heavy rain triggers
    if soil_saturated and terrain_type in ("RIVERINE_PLAIN", "AGRICULTURAL_PLAIN"):
        secondary_score += 25
        secondary_list.append("flood_escalation")

    secondary_score = min(secondary_score, 60)

    # 3. Composite Calculation
    escalation_score = int((traj_score * 0.60) + (secondary_score * 0.40))

    return min(escalation_score, 100), traj_score, secondary_score, secondary_list
