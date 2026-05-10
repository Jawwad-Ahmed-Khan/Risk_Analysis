# app/api/routes/assessment_controller.py
# ─────────────────────────────────────────────────────────────────
# Assessment controller for triggering risk analysis.
# Orchestrates the interaction between the main system payload
# and the reasoning agent.
# ─────────────────────────────────────────────────────────────────

import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Header
from agents import Runner

from app.models.input_models import BreachPayload
from app.models.output_models import RiskAssessmentReport
from app.agent.risk_agent import risk_agent
from app.core.config import settings
from app.core.exceptions import http_agent_error, http_unauthorized
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Assessment"])


def verify_api_key(x_api_key: str = Header(None)) -> None:
    """
    Dependency to verify the internal API key from request headers.
    """
    if not x_api_key or x_api_key != settings.internal_api_key:
        logger.warning("Unauthorized access attempt with invalid or missing API key")
        raise http_unauthorized()


@router.post(
    "/assess",
    response_model=RiskAssessmentReport,
    summary="Trigger Risk Analysis Assessment",
    description="Receives a disaster breach and runs the full risk analysis pipeline."
)
async def trigger_assessment(
    payload: BreachPayload,
    _auth: None = Depends(verify_api_key)
) -> RiskAssessmentReport:
    """
    Main endpoint to initiate a risk assessment for a disaster event.
    """
    assessment_id = str(uuid.uuid4())
    
    logger.info(
        f"Risk assessment triggered. assessment_id={assessment_id} | "
        f"breach_id={payload.breach_id} | disaster={payload.disaster_kind} | "
        f"location={payload.district}, {payload.province}"
    )
    
    # Prepare the comprehensive input for the agent
    agent_input = _build_agent_input(payload, assessment_id)
    
    try:
        # Execute the agent workflow
        # Position 1: agent, Position 2: input string
        result = await Runner.run(
            risk_agent,
            agent_input,
            max_turns=settings.openai_max_turns
        )
        
        # Extract the structured output enforced by the agent's output_type
        report: RiskAssessmentReport = result.final_output
        
        logger.info(
            f"Assessment completed successfully. assessment_id={assessment_id} | "
            f"risk_level={report.risk_level} | composite_score={report.composite_risk_score}"
        )
        
        return report

    except Exception as e:
        logger.error(f"Agent execution failed for assessment_id={assessment_id}: {str(e)}")
        raise http_agent_error(str(e))


def _build_agent_input(payload: BreachPayload, assessment_id: str) -> str:
    """
    Formats the complete situational context for the agent to begin its analysis.
    """
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    context = [
        f"--- RISK ASSESSMENT CASE: {assessment_id} ---",
        f"CURRENT TIME: {current_time}",
        "",
        "BREACH METRICS:",
        f"- ID: {payload.breach_id}",
        f"- Disaster Kind: {payload.disaster_kind.value}",
        f"- Observed Value: {payload.observed_value}",
        f"- Threshold Value: {payload.threshold_value}",
        f"- Severity: {payload.breach_severity.value}",
        f"- Metric Name: {payload.metric_name}",
        f"- Observation Time: {payload.observation_time}",
        f"- Is Forecast: {payload.is_forecast_breach}",
        f"- Forecast Horizon: {payload.forecast_horizon_h or 'N/A'}",
        "",
        "LOCATION CONTEXT:",
        f"- Name: {payload.location_name}",
        f"- District: {payload.district}",
        f"- Province: {payload.province.value}",
        f"- Latitude: {payload.latitude}",
        f"- Longitude: {payload.longitude}",
        f"- Source API: {payload.source_api.value}",
        "",
        "DATABASE LOOKUP HINTS:",
        f"- gauge_id: {payload.gauge_id or 'N/A'}",
        f"- usgs_event_id: {payload.usgs_event_id or 'N/A'}",
        f"- weather_location_id: {payload.weather_location_id or 'N/A'}",
        "",
        "MANDATORY INSTRUCTIONS:",
        "1. You MUST follow your 11-step execution workflow exactly.",
        f"2. You MUST use assessment_id='{assessment_id}' in your final output.",
        "3. Provide a data-driven, defensible risk score for the specified disaster kind.",
        "--- START ANALYSIS ---"
    ]
    
    return "\n".join(context)
