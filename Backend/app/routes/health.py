"""Health-check endpoint."""

from fastapi import APIRouter

from app.schemas.system import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok", version="1.0.0")
