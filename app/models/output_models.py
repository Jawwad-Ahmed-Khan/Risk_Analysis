# app/models/output_models.py
# ─────────────────────────────────────────────────────────────────
# Complete Pydantic output schema for the risk assessment report.
# Every field documented. Precaution Definer Agent reads this.
# ─────────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class DataConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SituationTrajectory(str, Enum):
    IMPROVING = "Improving"
    STABLE = "Stable"
    WORSENING = "Worsening"
    RAPIDLY_WORSENING = "Rapidly Worsening"


class ResponseUrgency(str, Enum):
    MONITOR = "Monitor"
    PREPARE = "Prepare"
    RESPOND = "Respond"
    EMERGENCY = "Emergency"


# ── NESTED MODELS ──────────────────────────────────────────────────

class TerrainAssessment(BaseModel):
    terrain_type: str
    terrain_source: str
    terrain_vulnerability_score: int = Field(..., ge=0, le=100)
    terrain_multiplier: float
    terrain_implications: List[str]
    slope_description: Optional[str] = None
    soil_type: Optional[str] = None
    vegetation_cover: Optional[str] = None


class HazardSeverityScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    base_score: int
    modifiers_applied: List[str]
    key_metric_name: str
    key_metric_value: str
    secondary_hazards_identified: List[str]
    justification: str


class PopulationBreakdown(BaseModel):
    total_population: int
    population_source: str
    population_density_per_sqkm: Optional[float]
    estimated_directly_affected: int
    estimation_method: str
    vulnerable_groups: Dict[str, int]
    poverty_rate_pct: float
    poverty_source: str
    outdoor_workers_estimate: Optional[int] = None


class InfrastructureAtRisk(BaseModel):
    hospitals_count: int
    hospital_beds_total: int
    hospital_beds_per_1000_population: float
    critical_hospitals: List[str]
    schools_count: int
    estimated_students_at_risk: int
    bridges_count: int
    critical_bridges: List[str]
    dams_count: int
    barrages_count: int
    dam_failure_risk: bool
    dam_failure_risk_reason: Optional[str]
    evacuation_centers_count: int
    evacuation_capacity_total: int
    evacuation_coverage_pct: float
    power_stations_at_risk: int
    water_treatment_at_risk: int
    total_critical_assets: int
    impact_radius_km_used: float


class ExposureScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    population_score: int
    infrastructure_score: int
    population_breakdown: PopulationBreakdown
    infrastructure_at_risk: InfrastructureAtRisk
    justification: str


class VulnerabilityScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    building_vulnerability_score: int
    building_stock_type: str
    building_stock_source: str
    kutcha_percentage_estimate: Optional[float]
    drainage_vulnerability_score: int
    drainage_quality_level: str
    infrastructure_quality_score: int
    poverty_vulnerability_score: int
    terrain_vulnerability_score: int
    component_scores: Dict[str, int]
    justification: str


class EscalationScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    is_worsening: bool
    trajectory_description: str
    current_trajectory_score: int
    secondary_disaster_score: int
    secondary_disasters_possible: List[str]
    escalation_probability_pct: float
    hours_until_peak_estimate: Optional[float]
    peak_estimate_basis: str
    justification: str


class ResponseCapacityScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    medical_capacity_score: int
    evacuation_capacity_score: int
    road_access_score: int
    ngo_presence_score: int
    road_status_description: str
    ngo_presence_description: str
    nearest_major_hospital_km: Optional[float]
    response_time_estimate_hours: Optional[float]
    justification: str


class WebSearchFinding(BaseModel):
    query_used: str
    key_findings: str
    sources_cited: List[str]
    confidence: str


class WebSearchFindings(BaseModel):
    terrain_geography: WebSearchFinding
    demographics_poverty: WebSearchFinding
    historical_disaster_context: WebSearchFinding
    current_ground_situation: WebSearchFinding
    disaster_specific_findings: List[WebSearchFinding]


class ImpactEstimates(BaseModel):
    estimated_population_affected: int
    estimation_confidence: DataConfidence
    estimated_deaths_range: str
    death_risk_level: str
    estimated_displaced_persons: int
    displacement_duration_estimate: str
    estimated_economic_damage_pkr: str
    estimated_economic_damage_usd: str
    economic_damage_confidence: DataConfidence
    agricultural_land_at_risk_acres: Optional[int]
    crop_loss_probability_pct: Optional[float]
    livestock_at_risk_description: Optional[str]


# ── MAIN REPORT ───────────────────────────────────────────────────

class RiskAssessmentReport(BaseModel):
    assessment_id: str
    breach_id: str
    disaster_kind: str
    breach_severity_received: str
    location_name: str
    district: str
    province: str
    latitude: float
    longitude: float
    observation_time: str
    is_forecast_breach: bool
    forecast_horizon_h: Optional[int]
    assessment_timestamp: str
    agent_version: str = "risk_analysis_v2.0"
    
    terrain_assessment: TerrainAssessment
    hazard_severity: HazardSeverityScore
    exposure: ExposureScore
    vulnerability: VulnerabilityScore
    escalation_risk: EscalationScore
    response_capacity: ResponseCapacityScore
    
    score_breakdown: Dict[str, float]
    composite_score_before_terrain: float
    terrain_multiplier_applied: float
    composite_risk_score: float
    override_applied: bool
    override_reason: Optional[str]
    risk_level: RiskLevel
    risk_level_justification: str
    
    impact_estimates: ImpactEstimates
    situation_trajectory: SituationTrajectory
    escalation_triggers: List[str]
    web_search_findings: WebSearchFindings
    
    recommended_response_urgency: ResponseUrgency
    critical_actions_needed: List[str]
    time_sensitive_actions: List[str]
    
    data_confidence: DataConfidence
    data_gaps: List[str]
    assumptions_made: List[str]
