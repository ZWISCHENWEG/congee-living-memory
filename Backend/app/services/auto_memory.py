"""Autonomous memory orchestrator (Phase 3).

Ties the classifier, semantic similarity lookup, and memory persistence together
so that memories are created / updated / deduplicated / forgotten automatically
during a conversation. The single entry point `process` is resilient: it logs
every step and never raises into the chat flow.
"""

import logging
import re

from fastapi import Depends

from app.config import get_settings
from app.schemas.memories import MemoryCreate
from app.schemas.memory_engine import MemoryAction
from app.services.memory import MemoryService, get_memory_service
from app.services.memory_extraction import (
    MemoryExtractionService,
    get_memory_extraction_service,
)
from app.services.search import SearchService, get_search_service

logger = logging.getLogger(__name__)


def _normalize(text: str) -> str:
    """Lowercase, strip punctuation/whitespace, collapse spaces — for detecting
    near-identical (true duplicate) memory strings."""
    return re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()


class AutoMemoryService:
    """Decides and applies the memory operation implied by a user message."""

    def __init__(
        self,
        extraction: MemoryExtractionService,
        search_service: SearchService,
        memory_service: MemoryService,
    ):
        self.extraction = extraction
        self.search_service = search_service
        self.memory_service = memory_service

    async def process(self, user_message: str) -> MemoryAction:
        """Run the full extract → dedup → conflict/update/insert/forget pipeline.

        Returns a `MemoryAction` describing the outcome. Never raises: on any
        unexpected error it logs and returns ``status="ignored"``.
        """
        try:
            return await self._process(user_message)
        except Exception as e:  # noqa: BLE001 - memory engine must not break chat
            logger.exception("Auto-memory pipeline failed, ignoring: %s", e)
            return MemoryAction(status="ignored", detail="internal error")

    async def _process(self, user_message: str) -> MemoryAction:
        extraction = await self.extraction.classify(user_message)

        if extraction.action == "none" or not extraction.memory:
            return MemoryAction(status="ignored")

        if extraction.action == "forget":
            return await self._handle_forget(extraction.memory)

        return await self._handle_save(extraction.memory, extraction.type, extraction.importance)

    async def _handle_forget(self, target: str) -> MemoryAction:
        """Locate the closest matching memory and delete it (Feature 7)."""
        settings = get_settings()
        matches = await self.search_service.find_similar(target, top_k=1)
        if not matches or (matches[0].score or 0.0) < settings.forget_threshold:
            logger.info("Forget request matched no stored memory: %r", target)
            return MemoryAction(status="ignored", memory=target, detail="no matching memory to forget")

        match = matches[0]
        self.memory_service.delete_memory(match.id)  # logs "Memory deleted"
        return MemoryAction(
            status="deleted",
            memory=match.content,
            memory_id=match.id,
            detail=f"matched at similarity {match.score}",
        )

    async def _handle_save(self, memory: str, mem_type: str, importance: float) -> MemoryAction:
        """Dedup, then conflict/update, else insert (Features 4, 5, 6)."""
        settings = get_settings()
        matches = await self.search_service.find_similar(memory, top_k=1)
        top = matches[0] if matches else None
        top_score = (top.score or 0.0) if top else 0.0
        logger.info("Semantic search complete (top similarity=%.4f)", top_score)

        # Feature 4: a true duplicate is a near-identical string, not merely a
        # highly-similar one. "I live in Surat" vs "I live in Ahmedabad" can score
        # above the duplicate threshold yet is an UPDATE, not a duplicate — so we
        # require both high similarity AND normalized-equal text here.
        if (
            top
            and top_score >= settings.duplicate_threshold
            and _normalize(memory) == _normalize(top.content)
        ):
            logger.info("Duplicate detected for %r (similarity=%.4f)", memory, top_score)
            return MemoryAction(
                status="duplicate",
                memory=top.content,
                memory_id=top.id,
                type=mem_type,
                importance=importance,
                detail=f"similarity {top_score}",
            )

        # Features 5 & 6: similar-but-different -> potential update / conflict.
        if top and top_score >= settings.conflict_threshold:
            decision = await self.extraction.decide_conflict(existing=top.content, new=memory)
            if decision.replace and decision.confidence > settings.conflict_confidence:
                updated = await self.memory_service.update_memory(
                    memory_id=top.id, content=memory, type=mem_type, importance=importance
                )
                if updated is not None:
                    return MemoryAction(
                        status="updated",
                        memory=memory,
                        memory_id=top.id,
                        type=mem_type,
                        importance=importance,
                        detail=decision.reason,
                    )
                # Fell through (memory vanished) — treat as fresh insert below.
            else:
                logger.info("Conflict detected for %r (pending confirmation)", memory)
                return MemoryAction(
                    status="conflict",
                    memory=memory,
                    memory_id=top.id,
                    type=mem_type,
                    importance=importance,
                    detail=(
                        f"conflicts with existing '{top.content}' "
                        f"(replace confidence {decision.confidence:.2f})"
                    ),
                )

        # Otherwise: brand-new memory.
        created = await self.memory_service.create_memory(
            MemoryCreate(content=memory, type=mem_type, importance=importance)
        )
        return MemoryAction(
            status="created",
            memory=created.content,
            memory_id=created.id,
            type=mem_type,
            importance=importance,
        )


def get_auto_memory_service(
    extraction: MemoryExtractionService = Depends(get_memory_extraction_service),
    search_service: SearchService = Depends(get_search_service),
    memory_service: MemoryService = Depends(get_memory_service),
) -> AutoMemoryService:
    return AutoMemoryService(extraction, search_service, memory_service)
