# app/agent/scoring/response_scorer.py
# ─────────────────────────────────────────────────────────────────
# Logic for assessing regional response and relief capacity.
# ─────────────────────────────────────────────────────────────────

def score_response_capacity(
    hospital_beds: int,
    population: int,
    evacuation_capacity: int,
    road_access_description: str,
    ngo_presence_description: str
) -> tuple[int, int, int, int, int]:
    """
    Returns: (response_score, medical_score, evacuation_score, road_score, ngo_score)
    NOTE: Higher score = LOWER capacity = MORE vulnerable
    """
    
    # 1. Medical Capacity
    if population == 0 or hospital_beds == 0:
        med_score = 95
    else:
        beds_per_1000 = (hospital_beds / population) * 1000
        if beds_per_1000 > 2.0: med_score = 15
        elif beds_per_1000 >= 1.0: med_score = 35
        elif beds_per_1000 >= 0.5: med_score = 60
        elif beds_per_1000 >= 0.2: med_score = 80
        else: med_score = 95

    # 2. Evacuation Capacity
    if population == 0 or evacuation_capacity == 0:
        evac_score = 95
    else:
        ratio = (evacuation_capacity / population)
        if ratio > 0.20: evac_score = 10
        elif ratio >= 0.10: evac_score = 30
        elif ratio >= 0.05: evac_score = 55
        elif ratio >= 0.02: evac_score = 75
        else: evac_score = 95

    # 3. Road Score
    road_desc = road_access_description.lower()
    if "national_highway" in road_desc or "open" in road_desc:
        road_score = 10
    elif "provincial" in road_desc:
        road_score = 30
    elif "district" in road_desc:
        road_score = 55
    elif "village" in road_desc or "track" in road_desc:
        road_score = 75
    elif "blocked" in road_desc or "closed" in road_desc:
        road_score = 95
    else:
        road_score = 55

    # 4. NGO Score
    ngo_desc = ngo_presence_description.lower()
    if "multiple" in ngo_desc or "several" in ngo_desc:
        ngo_score = 10
    elif "one" in ngo_desc or "single" in ngo_desc:
        ngo_score = 35
    elif "nearby" in ngo_desc or "province" in ngo_desc:
        ngo_score = 60
    elif "none" in ngo_desc or "unknown" in ngo_desc:
        ngo_score = 85
    else:
        ngo_score = 60

    # 5. Composite Calculation
    response_score = int(
        (med_score * 0.30) +
        (evac_score * 0.25) +
        (road_score * 0.25) +
        (ngo_score * 0.20)
    )

    return min(response_score, 100), med_score, evac_score, road_score, ngo_score
