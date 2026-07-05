import json
import logging
import uuid
from datetime import UTC, datetime

from fastapi import Depends

from app.schemas.memories import MemoriesResponse, MemoryCreate, MemorySchema, MetaSchema
from app.services.embedding import (
    EmbeddingGenerationError,
    EmbeddingProvider,
    EmbeddingProviderUnavailableError,
    get_embedding_provider,
)
from app.services.memory_repository import MemoryRepository, get_memory_repository

logger = logging.getLogger(__name__)


class MemoryService:
    """Service orchestrating memory creation, retrieval, and deletion."""

    def __init__(self, embedding_provider: EmbeddingProvider, repository: MemoryRepository):
        self.embedding_provider = embedding_provider
        self.repository = repository

    async def _embed(self, content: str) -> str | None:
        """Generate a JSON-encoded embedding, or None on failure (resilient)."""
        logger.info("Using EmbeddingProvider: %s", self.embedding_provider.__class__.__name__)
        try:
            embedding = await self.embedding_provider.generate_embedding(content)
            logger.info("Embedding generated successfully (%d dimensions)", len(embedding))
            return json.dumps(embedding)
        except (EmbeddingGenerationError, EmbeddingProviderUnavailableError) as e:
            logger.warning(
                "Failed to generate embedding (Provider: %s). Storing NULL embedding. Reason: %s",
                self.embedding_provider.name,
                type(e).__name__,
            )
            return None

    async def create_memory(self, memory: MemoryCreate) -> MemorySchema:
        """Create a new memory, generate its embedding, and store it."""
        mem_id = f"mem_{uuid.uuid4().hex[:12]}"
        created_at = datetime.now(UTC).isoformat()
        tags_json = json.dumps(memory.tags) if memory.tags else "[]"
        mem_type = memory.type or "other"
        importance = memory.importance if memory.importance is not None else 0.5

        embedding_json = await self._embed(memory.content)

        self.repository.insert_memory(
            memory_id=mem_id,
            content=memory.content,
            created_at=created_at,
            tags_json=tags_json,
            embedding_json=embedding_json,
            type=mem_type,
            importance=importance,
        )

        if embedding_json:
            logger.info("Successfully wrote embedding to SQLite for memory %s", mem_id)
        else:
            logger.info("Wrote memory %s to SQLite without an embedding", mem_id)
        logger.info("Memory inserted: %s (type=%s, importance=%.2f)", mem_id, mem_type, importance)

        return MemorySchema(
            id=mem_id,
            content=memory.content,
            created_at=created_at,
            tags=memory.tags or [],
            type=mem_type,
            importance=importance,
            usage_count=0,
        )

    async def update_memory(
        self, memory_id: str, content: str, type: str, importance: float
    ) -> MemorySchema | None:
        """Replace an existing memory's content/embedding/metadata in place.

        Returns the updated memory, or None if `memory_id` does not exist.
        """
        existing = self.repository.get_by_id(memory_id)
        if existing is None:
            logger.warning("Update requested for missing memory %s", memory_id)
            return None

        updated_at = datetime.now(UTC).isoformat()
        embedding_json = await self._embed(content)
        self.repository.update_memory(
            memory_id=memory_id,
            content=content,
            embedding_json=embedding_json,
            type=type,
            importance=importance,
            updated_at=updated_at,
        )
        logger.info("Existing memory updated: %s", memory_id)

        tags = json.loads(existing["tags"]) if existing["tags"] else []
        return MemorySchema(
            id=memory_id,
            content=content,
            created_at=existing["created_at"],
            tags=tags,
            type=type,
            importance=importance,
            usage_count=existing["usage_count"],
            updated_at=updated_at,
        )

    def mark_used(self, memory_ids: list[str]) -> None:
        """Increment usage_count and stamp last_accessed for retrieved memories
        (Features 8 & 9). Best-effort: logs but never raises into the chat flow."""
        if not memory_ids:
            return
        last_accessed = datetime.now(UTC).isoformat()
        for memory_id in memory_ids:
            try:
                self.repository.mark_used(memory_id, last_accessed)
            except Exception as e:  # noqa: BLE001 - usage tracking must not break chat
                logger.warning("Failed to mark memory %s as used: %s", memory_id, e)

    def delete_memory(self, memory_id: str) -> None:
        """Delete a memory by ID."""
        self.repository.delete_memory(memory_id)
        logger.info("Memory deleted: %s", memory_id)

    def get_memories(self, page: int, limit: int, search: str | None = None) -> MemoriesResponse:
        """Retrieve paginated memories."""
        rows, total = self.repository.get_memories(page, limit, search)

        data = []
        for row in rows:
            tags = json.loads(row["tags"]) if row["tags"] else []
            data.append(
                MemorySchema(
                    id=row["id"],
                    content=row["content"],
                    created_at=row["created_at"],
                    tags=tags,
                    type=row["type"],
                    importance=row["importance"],
                    usage_count=row["usage_count"],
                    last_accessed=row["last_accessed"],
                    updated_at=row["updated_at"],
                )
            )

        return MemoriesResponse(data=data, meta=MetaSchema(total=total, page=page, limit=limit))


def get_memory_service(
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
    repository: MemoryRepository = Depends(get_memory_repository),
) -> MemoryService:
    return MemoryService(embedding_provider, repository)
