# app/agent/risk_agent.py
# ─────────────────────────────────────────────────────────────────
# Risk Analysis Agent definition using OpenAI Agents SDK.
# This module wires together the system prompt, data tools,
# and the output schema to create a specialized reasoning agent.
# ─────────────────────────────────────────────────────────────────

from agents import (
    Agent,
    WebSearchTool,
    AgentOutputSchema,
    ModelSettings,
    ModelRetrySettings,
    retry_policies,
)

from app.agent.system_prompt import RISK_ANALYSIS_SYSTEM_PROMPT
from app.agent.tools.location_tool import get_location_data
from app.agent.tools.infrastructure_tool import get_infrastructure_at_risk
from app.agent.tools.disaster_data_tool import get_current_disaster_data
from app.models.output_models import RiskAssessmentReport
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)


def create_risk_analysis_agent() -> Agent:
    """
    Creates and returns the ClimaSync Risk Analysis Agent.

    The agent is configured with:
    - Specialized instructions for Pakistan-specific disaster risk analysis.
    - Custom tools for database lookups (locations, infrastructure, time-series data).
    - Built-in WebSearchTool for filling situational data gaps.
    - Structured output enforcement using the RiskAssessmentReport Pydantic model.
    - Runner-managed retry with exponential backoff for 429 rate-limit resilience.

    Returns:
        Agent: A configured instance of the ClimaSync Risk Analysis Agent.
    """
    agent = Agent(
        name="ClimaSync Risk Analysis Agent",
        model=settings.openai_model,
        instructions=RISK_ANALYSIS_SYSTEM_PROMPT,
        tools=[
            get_location_data,
            get_infrastructure_at_risk,
            get_current_disaster_data,
            WebSearchTool(),
        ],
        output_type=AgentOutputSchema(RiskAssessmentReport, strict_json_schema=False),
        model_settings=ModelSettings(
            retry=ModelRetrySettings(
                max_retries=4,
                backoff={
                    "initial_delay": 2.0,
                    "max_delay": 30.0,
                    "multiplier": 2.0,
                    "jitter": True,
                },
                policy=retry_policies.any(
                    retry_policies.provider_suggested(),
                    retry_policies.retry_after(),
                    retry_policies.network_error(),
                    retry_policies.http_status([408, 429, 500, 502, 503, 504]),
                ),
            )
        ),
    )

    logger.info(
        f"Risk Analysis Agent created successfully. "
        f"Model: {settings.openai_model}, "
        f"Output Type: {RiskAssessmentReport.__name__}"
    )

    return agent


# ─────────────────────────────────────────────────────────────────
# Module-level singleton instance
# ─────────────────────────────────────────────────────────────────
risk_agent = create_risk_analysis_agent()
