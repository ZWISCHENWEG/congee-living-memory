from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

class MemoryRepository(ABC):
    """Abstract base class for memory persistence."""

    @abstractmethod
    def insert_memory(
        self,
        memory_id: str,
        content: str,
        created_at: str,
        tags_json: str,
        embedding_json: Optional[str],
        type: str = "other",
        importance: float = 0.5,
    ) -> None:
        """Insert a new memory into the database.

        `type` and `importance` default to the Phase 1/2 values so existing
        callers that omit them continue to work unchanged.
        """
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str) -> None:
        """Delete a memory by its ID."""
        pass

    @abstractmethod
    def get_memories(self, page: int, limit: int, search: Optional[str]) -> Tuple[List[dict], int]:
        """Fetch a paginated list of memories and the total count.

        Returns:
            Tuple containing:
            - List of dictionaries with keys: id, content, created_at, tags (JSON string),
              and the Phase 3 columns (type, importance, usage_count, last_accessed, updated_at)
            - Total count of records matching the search (if any)
        """
        pass

    @abstractmethod
    def get_by_id(self, memory_id: str) -> Optional[dict]:
        """Fetch a single memory row by ID, or None if it does not exist."""
        pass

    @abstractmethod
    def update_memory(
        self,
        memory_id: str,
        content: str,
        embedding_json: Optional[str],
        type: str,
        importance: float,
        updated_at: str,
    ) -> None:
        """Replace the content/embedding/category/importance of an existing memory
        in place (Feature 5 & 6). Preserves id, created_at, and usage counters."""
        pass

    @abstractmethod
    def mark_used(self, memory_id: str, last_accessed: str) -> None:
        """Record that a memory was retrieved: increment usage_count and stamp
        last_accessed (Features 8 & 9)."""
        pass
