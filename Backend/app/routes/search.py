from fastapi import APIRouter, Depends, Query

from app.schemas.search import SearchResponse
from app.services.search import SearchService, get_search_service

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search_memories(
    q: str = Query(..., min_length=1), search_service: SearchService = Depends(get_search_service)
) -> SearchResponse:
    results = await search_service.search(q)
    return SearchResponse(results=results)
