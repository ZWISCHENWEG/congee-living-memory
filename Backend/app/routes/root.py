"""Root endpoint."""

from fastapi import APIRouter

from app.schemas.system import RootResponse

router = APIRouter(tags=["system"])


@router.get("/", response_model=RootResponse)
async def read_root() -> RootResponse:
    """Return basic project status."""
    return RootResponse(project="Chronos", status="running")
