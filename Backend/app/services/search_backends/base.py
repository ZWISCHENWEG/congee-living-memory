from abc import ABC, abstractmethod
from typing import List, Optional
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
        query_embedding: Optional[List[float]],
        query_text: str,
        limit: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[SearchResultSchema]:
        """Search memories synchronously.
        
        If query_embedding is provided, the backend should attempt a semantic search.
        If it is None, or if semantic search fails to yield valid results,
        it should fall back to a keyword/LIKE search using query_text.
        """
        pass
