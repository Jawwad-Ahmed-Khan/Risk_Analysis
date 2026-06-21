# app/models/output_models.py
# ─────────────────────────────────────────────────────────────────
# Complete Pydantic output schema for the risk assessment report.
# Every field documented. Precaution Definer Agent reads this.
# ─────────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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
    terrain_vulnerability_score: int = Field(..., ge=0, le=200)
    terrain_multiplier: float
    terrain_implications: List[str]
    slope_description: Optional[str] = None
    soil_type: Optional[str] = None
    vegetation_cover: Optional[str] = None


class HazardSeverityScore(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=200)
    base_score: Optional[float] = None
    modifiers_applied: List[str] = []
    key_metric_name: str
    key_metric_value: str
    secondary_hazards_identified: List[str]
    justification: str


class VulnerableGroups(BaseModel):
    elderly_pct: Optional[float] = None
    children_pct: Optional[float] = None
    women_pct: Optional[float] = None
    disabled_pct: Optional[float] = None
    other_groups_description: Optional[str] = None

class PopulationBreakdown(BaseModel):
    total_population: int
    population_source: str
    population_density_per_sqkm: Optional[float] = None
    estimated_directly_affected: Optional[int] = None
    estimation_method: str = "estimate"
    vulnerable_groups: Optional[VulnerableGroups] = None
    poverty_rate_pct: Optional[float] = None
    poverty_source: Optional[str] = "default"
    outdoor_workers_estimate: Optional[int] = None


class InfrastructureAtRisk(BaseModel):
    hospitals_count: Optional[int] = None
    hospital_beds_total: Optional[int] = None
    hospital_beds_per_1000_population: Optional[float] = None
    critical_hospitals: List[str] = []
    schools_count: Optional[int] = None
    estimated_students_at_risk: Optional[int] = None
    bridges_count: Optional[int] = None
    critical_bridges: List[str] = []
    dams_count: Optional[int] = None
    barrages_count: Optional[int] = None
    dam_failure_risk: bool = False
    dam_failure_risk_reason: Optional[str] = None
    evacuation_centers_count: Optional[int] = None
    evacuation_capacity_total: Optional[int] = None
    evacuation_coverage_pct: Optional[float] = None
    power_stations_at_risk: Optional[int] = None
    water_treatment_at_risk: Optional[int] = None
    total_critical_assets: Optional[int] = None
    impact_radius_km_used: Optional[float] = None


class ExposureScore(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=200)
    population_score: Optional[float] = None
    infrastructure_score: Optional[float] = None
    population_breakdown: PopulationBreakdown
    infrastructure_at_risk: InfrastructureAtRisk
    justification: str


class VulnerabilityComponentScores(BaseModel):
    building: Optional[float] = None
    drainage: Optional[float] = None
    infrastructure: Optional[float] = None
    poverty: Optional[float] = None
    terrain: Optional[float] = None

class VulnerabilityScore(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=200)
    building_vulnerability_score: Optional[float] = None
    building_stock_type: Optional[str] = None
    building_stock_source: Optional[str] = None
    kutcha_percentage_estimate: Optional[float] = None
    drainage_vulnerability_score: Optional[float] = None
    drainage_quality_level: Optional[str] = None
    infrastructure_quality_score: Optional[float] = None
    poverty_vulnerability_score: Optional[float] = None
    terrain_vulnerability_score: Optional[float] = Field(None, ge=0, le=200)
    component_scores: Optional[VulnerabilityComponentScores] = None
    justification: str


class EscalationScore(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=200)
    is_worsening: Optional[bool] = None
    trajectory_description: str
    current_trajectory_score: Optional[float] = None
    secondary_disaster_score: Optional[float] = None
    secondary_disasters_possible: List[str] = []
    escalation_probability_pct: Optional[float] = None
    hours_until_peak_estimate: Optional[float] = None
    peak_estimate_basis: Optional[str] = None
    justification: str


class ResponseCapacityScore(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=200)
    medical_capacity_score: Optional[float] = None
    evacuation_capacity_score: Optional[float] = None
    road_access_score: Optional[float] = None
    ngo_presence_score: Optional[float] = None
    road_status_description: Optional[str] = None
    ngo_presence_description: Optional[str] = None
    nearest_major_hospital_km: Optional[float] = None
    response_time_estimate_hours: Optional[float] = None
    justification: str


class WebSearchFinding(BaseModel):
    query_used: str
    key_findings: str
    sources_cited: List[str]
    confidence: str


class WebSearchFindings(BaseModel):
    terrain_geography: Optional[WebSearchFinding] = None
    demographics_poverty: Optional[WebSearchFinding] = None
    historical_disaster_context: Optional[WebSearchFinding] = None
    current_ground_situation: Optional[WebSearchFinding] = None
    disaster_specific_findings: List[WebSearchFinding] = []


class ImpactEstimates(BaseModel):
    estimated_population_affected: Optional[int] = None
    estimation_confidence: DataConfidence
    estimated_deaths_range: Optional[str] = None
    death_risk_level: Optional[str] = None
    estimated_displaced_persons: Optional[int] = None
    displacement_duration_estimate: Optional[str] = None
    estimated_economic_damage_pkr: Optional[str] = None
    estimated_economic_damage_usd: Optional[str] = None
    economic_damage_confidence: DataConfidence
    agricultural_land_at_risk_acres: Optional[int] = None
    crop_loss_probability_pct: Optional[float] = None
    livestock_at_risk_description: Optional[str] = None


# ── MAIN REPORT ───────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    hazard: Optional[float] = None
    exposure: Optional[float] = None
    vulnerability: Optional[float] = None
    escalation: Optional[float] = None
    response: Optional[float] = None

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
    
    score_breakdown: ScoreBreakdown
    composite_score_before_terrain: Optional[float] = None
    terrain_multiplier_applied: Optional[float] = None
    composite_risk_score: Optional[float] = None
    override_applied: Optional[bool] = False
    override_reason: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    risk_level_justification: Optional[str] = None
    
    impact_estimates: ImpactEstimates
    situation_trajectory: SituationTrajectory
    escalation_triggers: List[str]
    web_search_findings: WebSearchFindings
    
    recommended_response_urgency: Optional[ResponseUrgency] = None
    critical_actions_needed: List[str] = []
    time_sensitive_actions: List[str] = []
    
    data_confidence: Optional[DataConfidence] = None
    data_gaps: List[str] = []
    assumptions_made: List[str] = []
