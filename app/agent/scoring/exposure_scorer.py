# app/agent/scoring/exposure_scorer.py
# ─────────────────────────────────────────────────────────────────
# Logic for calculating population and infrastructure exposure.
# ─────────────────────────────────────────────────────────────────

def score_exposure(
    population: int,
    population_density: float,
    hospitals_count: int,
    hospital_beds: int,
    schools_count: int,
    critical_assets_count: int,
    dams_count: int,
    barrages_count: int,
    bridges_critical_count: int
) -> tuple[int, int, int]:
    """
    Returns: (exposure_score, population_score, infrastructure_score)
    """
    # 1. Population Score
    if population < 50000: pop_score = 10
    elif population < 100000: pop_score = 25
    elif population < 300000: pop_score = 40
    elif population < 600000: pop_score = 60
    elif population < 1000000: pop_score = 75
    elif population < 3000000: pop_score = 88
    else: pop_score = 100

    # Density modifier
    if population_density > 10000: pop_score += 15
    elif population_density > 5000: pop_score += 10
    elif population_density > 1000: pop_score += 5
    
    pop_score = min(pop_score, 100)

    # 2. Infrastructure Score
    if hospitals_count == 0: infra_score = 100
    elif hospitals_count <= 2: infra_score = 70
    elif hospitals_count <= 5: infra_score = 45
    elif hospitals_count <= 10: infra_score = 25
    else: infra_score = 10

    # Additive critical modifiers
    # Note: Using the count of dams, barrages, and critical bridges/hospitals
    dam_barrage_mod = min((dams_count + barrages_count) * 25, 50)
    infra_score += dam_barrage_mod
    
    # We assume critical_hospitals refers to a filtered list or count of high-priority sites
    # For this function, we use bridges_critical_count as a proxy for specific asset weights
    bridge_mod = min(bridges_critical_count * 10, 20)
    infra_score += bridge_mod
    
    # hospital_crit_mod based on context of asset importance
    # Here we simplify: if critical_assets_count > 0, we apply a base weight
    infra_score += min(critical_assets_count * 15, 30)

    infra_score = min(infra_score, 100)

    # 3. Composite Exposure
    exposure_score = int((pop_score * 0.55) + (infra_score * 0.45))
    
    return min(exposure_score, 100), pop_score, infra_score
