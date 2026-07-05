from app.services.memory_repository.base import MemoryRepository
from app.services.memory_repository.sqlite import SQLiteMemoryRepository


def get_memory_repository() -> MemoryRepository:
    """Factory to return the configured Memory Repository."""
    return SQLiteMemoryRepository()
