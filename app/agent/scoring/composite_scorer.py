# app/agent/scoring/composite_scorer.py
# ─────────────────────────────────────────────────────────────────
# Final risk score integration and level classification.
# ─────────────────────────────────────────────────────────────────

from app.models.output_models import RiskLevel

WEIGHTS = {
    "hazard_severity": 0.25,
    "exposure": 0.25,
    "vulnerability": 0.20,
    "escalation_risk": 0.15,
    "response_capacity": 0.15
}

TERRAIN_MULTIPLIERS = {
    "MOUNTAIN": 1.20,
    "HIGHLAND": 1.10,
    "COASTAL": 1.15,
    "URBAN": 1.10,
    "RIVERINE_PLAIN": 1.10,
    "DESERT": 1.08,
    "AGRICULTURAL_PLAIN": 1.00,
    "unknown": 1.05
}

def compute_composite_score(
    hazard_score: int,
    exposure_score: int,
    vulnerability_score: int,
    escalation_score: int,
    response_capacity_score: int,
    terrain_type: str,
    usgs_alert_level: str = None,
    tsunami_flag: bool = False,
    dam_failure_risk: bool = False,
    flood_status: str = None,
    magnitude: float = None,
    population: int = None
) -> tuple[float, float, float, bool, str | None, RiskLevel]:
    """
    Returns: (score_before_terrain, terrain_multiplier, final_score, 
              override_applied, override_reason, risk_level)
    """
    # 1. Weighted Sum
    score_before_terrain = (
        (hazard_score * WEIGHTS["hazard_severity"]) +
        (exposure_score * WEIGHTS["exposure"]) +
        (vulnerability_score * WEIGHTS["vulnerability"]) +
        (escalation_score * WEIGHTS["escalation_risk"]) +
        (response_capacity_score * WEIGHTS["response_capacity"])
    )

    # 2. Apply Terrain Multiplier
    multiplier = TERRAIN_MULTIPLIERS.get(terrain_type.upper(), 1.05)
    final_score = score_before_terrain * multiplier
    
    # 3. Apply Mandatory Override Rules
    override_applied = False
    override_reason = None
    min_score = 0

    if usgs_alert_level == "red" or tsunami_flag:
        min_score = 75
        override_reason = "USGS Red Alert or Tsunami risk detected"
    elif dam_failure_risk and magnitude and magnitude >= 5.0:
        min_score = 75
        override_reason = "Dam failure risk in seismic impact zone"
    elif flood_status == "emergency":
        min_score = 50
        override_reason = "Official flood emergency status active"
    elif magnitude and magnitude >= 7.0:
        min_score = 75
        override_reason = "Extreme magnitude earthquake detected"
    elif population and population > 1000000:
        min_score = 50
        override_reason = "Mass population (>1M) exposure in breach zone"

    if final_score < min_score:
        final_score = min_score
        override_applied = True

    final_score = min(final_score, 100.0)

    # 4. Assign Risk Level
    if final_score < 25:
        level = RiskLevel.LOW
    elif final_score < 50:
        level = RiskLevel.MEDIUM
    elif final_score < 75:
        level = RiskLevel.HIGH
    else:
        level = RiskLevel.EXTREME

    return (
        float(score_before_terrain),
        float(multiplier),
        float(final_score),
        override_applied,
        override_reason,
        level
    )
