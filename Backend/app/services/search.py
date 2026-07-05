import logging
from fastapi import Depends
from app.schemas.search import SearchResultSchema
from typing import List
from app.services.embedding import get_embedding_provider, EmbeddingProvider, EmbeddingGenerationError, EmbeddingProviderUnavailableError
from app.services.search_backends import SearchBackend
from app.services.search_backends.factory import get_search_backend

logger = logging.getLogger(__name__)

class SearchService:
    """Service for orchestrating semantic memory search and retrieval."""
    
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        backend: SearchBackend
    ):
        self.embedding_provider = embedding_provider
        self.backend = backend
        
    async def search(self, query_text: str) -> List[SearchResultSchema]:
        """Search memories using semantic embeddings, falling back to keyword search."""
        
        query_embedding = None
        try:
            logger.info("Generating query embedding...")
            query_embedding = await self.embedding_provider.generate_embedding(query_text)
            if query_embedding:
                logger.info("Embedding generated successfully")
                logger.info("Embedding dimensions: %d", len(query_embedding))
        except (EmbeddingGenerationError, EmbeddingProviderUnavailableError) as e:
            logger.warning("Embedding generation failed for provider %s: %s", self.embedding_provider.name, type(e).__name__)
            # Safely continue to fallback
            
        results = self.backend.search(query_embedding, query_text)
        return results

    async def find_similar(self, text: str, top_k: int = 5) -> List[SearchResultSchema]:
        """Return the top_k memories by raw cosine similarity to `text`.

        Used by the autonomous memory engine for duplicate/conflict/forget
        matching. Returns an empty list if no embedding can be generated.
        """
        try:
            query_embedding = await self.embedding_provider.generate_embedding(text)
        except (EmbeddingGenerationError, EmbeddingProviderUnavailableError) as e:
            logger.warning(
                "Similarity lookup embedding failed for provider %s: %s",
                self.embedding_provider.name,
                type(e).__name__,
            )
            return []
        return self.backend.similarity_search(query_embedding, top_k=top_k)

def get_search_service(
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
    backend: SearchBackend = Depends(get_search_backend)
) -> SearchService:
    return SearchService(embedding_provider, backend)
