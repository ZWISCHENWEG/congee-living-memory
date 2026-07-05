"""Conflict resolution endpoint (Phase 3, Feature 6 tail).

When a chat turn returns ``memory_action.status == "conflict"``, the automatic
engine declined to auto-replace an existing memory. The frontend confirms the
user's intent and calls this endpoint to either apply the replacement or keep
the existing memory unchanged.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.memories import MemorySchema
from app.schemas.memory_engine import ConflictResolution, MemoryAction
from app.services.memory import MemoryService, get_memory_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["memories"])


@router.post("/memory/resolve-conflict", response_model=MemoryAction)
async def resolve_conflict(
    resolution: ConflictResolution,
    memory_service: MemoryService = Depends(get_memory_service),
) -> MemoryAction:
    """Apply or reject a pending memory conflict."""
    if resolution.decision == "keep":
        logger.info("Conflict resolution: keeping existing memory %s", resolution.existing_id)
        return MemoryAction(
            status="ignored",
            memory_id=resolution.existing_id,
            detail="user kept the existing memory",
        )

    updated: MemorySchema | None = await memory_service.update_memory(
        memory_id=resolution.existing_id,
        content=resolution.new_content,
        type=resolution.type,
        importance=resolution.importance,
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found.")

    return MemoryAction(
        status="updated",
        memory=updated.content,
        memory_id=updated.id,
        type=updated.type,
        importance=updated.importance,
        detail="user confirmed replacement",
    )
