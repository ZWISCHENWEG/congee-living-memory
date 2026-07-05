from app.config import get_settings
from app.services.search_backends.base import SearchBackend
from app.services.search_backends.sqlite import SQLiteSearchBackend

def get_search_backend() -> SearchBackend:
    """Factory to instantiate and return the configured Search Backend."""
    settings = get_settings()
    return SQLiteSearchBackend(
        default_limit=settings.search_limit,
        default_threshold=settings.similarity_threshold
    )
