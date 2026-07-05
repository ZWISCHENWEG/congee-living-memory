from abc import ABC, abstractmethod

class EmbeddingProviderUnavailableError(Exception):
    """Raised when the embedding provider is not configured or unavailable."""
    pass

class EmbeddingGenerationError(Exception):
    """Raised when the embedding provider fails to generate an embedding."""
    pass

class EmbeddingProvider(ABC):
    """Abstract base class for semantic embedding providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the embedding provider."""
        pass
        
    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate a vector embedding for the given text."""
        pass
