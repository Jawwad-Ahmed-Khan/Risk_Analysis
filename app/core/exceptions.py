# app/core/exceptions.py
# ─────────────────────────────────────────────────────────────────
# Custom exception hierarchy and FastAPI HTTP factory functions.
# ─────────────────────────────────────────────────────────────────

from fastapi import HTTPException, status


class RiskAgentError(Exception):
    """Base exception for all risk agent errors."""
    pass


class DatabaseConnectionError(RiskAgentError):
    """Cannot connect to collection database."""
    pass


class LocationNotFoundError(RiskAgentError):
    """Location not found in pakistan_locations table."""
    pass


class DisasterDataNotFoundError(RiskAgentError):
    """No disaster data found for given identifiers."""
    pass


class AgentExecutionError(RiskAgentError):
    """Agent failed to complete assessment."""
    pass


class InvalidInputError(RiskAgentError):
    """Input payload is invalid or incomplete."""
    pass


class ScoringError(RiskAgentError):
    """Error during risk score computation."""
    pass


# ── FastAPI HTTPException Factory Functions ─────────────────────────

def http_location_not_found(district: str) -> HTTPException:
    """Returns a 404 Not Found exception for missing locations."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Location context not found for district: {district}"
    )


def http_agent_error(detail: str) -> HTTPException:
    """Returns a 500 Internal Server Error exception for agent failures."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Agent execution failed: {detail}"
    )


def http_unauthorized() -> HTTPException:
    """Returns a 403 Forbidden exception for invalid internal API keys."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid or missing internal API key"
    )
