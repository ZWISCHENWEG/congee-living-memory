from abc import ABC, abstractmethod

from app.schemas.search import SearchResultSchema


class SearchBackend(ABC):
    """Abstract base class for search backends."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the search backend."""
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: list[float] | None,
        query_text: str,
        limit: int | None = None,
        similarity_threshold: float | None = None,
    ) -> list[SearchResultSchema]:
        """Search memories synchronously.

        If query_embedding is provided, the backend should attempt a semantic search.
        If it is None, or if semantic search fails to yield valid results,
        it should fall back to a keyword/LIKE search using query_text.
        """
        pass

    @abstractmethod
    def similarity_search(
        self,
        query_embedding: list[float] | None,
        top_k: int = 5,
    ) -> list[SearchResultSchema]:
        """Return the top_k memories by *raw cosine similarity* (score = cosine).

        Unlike `search`, this applies no threshold and no composite ranking — it
        is used by the autonomous memory engine to detect duplicates, conflicts,
        and forget-targets, which are calibrated against pure cosine similarity.
        Returns an empty list if no query embedding is available.
        """
        pass
