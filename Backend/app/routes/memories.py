import json
from fastapi import APIRouter, Response, status, Depends
from typing import Optional

from app.schemas.memories import MemorySchema, MemoriesResponse, MetaSchema, MemoryCreate
from app.services.memory import get_memory_service, MemoryService

router = APIRouter(tags=["memories"])

@router.get("/memories", response_model=MemoriesResponse)
def get_memories(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    memory_service: MemoryService = Depends(get_memory_service)
):
    return memory_service.get_memories(page, limit, search)

@router.post("/memory", response_model=MemorySchema, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory: MemoryCreate,
    memory_service: MemoryService = Depends(get_memory_service)
):
    return await memory_service.create_memory(memory)

@router.delete("/memory/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(
    id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    memory_service.delete_memory(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
