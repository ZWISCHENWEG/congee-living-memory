"""System-level response schemas."""

from pydantic import BaseModel


class RootResponse(BaseModel):
    """Response for the root endpoint."""

    project: str
    status: str


class HealthResponse(BaseModel):
    """Response for the health-check endpoint."""

    status: str
    version: str
