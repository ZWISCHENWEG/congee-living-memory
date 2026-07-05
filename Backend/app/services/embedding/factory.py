from app.config import get_settings
from app.services.embedding.base import EmbeddingProvider, EmbeddingProviderUnavailableError
from app.services.embedding.gemini import GeminiEmbeddingProvider

def get_embedding_provider() -> EmbeddingProvider:
    """Factory to instantiate and return the configured Embedding Provider."""
    settings = get_settings()
    
    if not settings.gemini_configured:
        raise EmbeddingProviderUnavailableError("Embedding provider is not configured.")
        
    return GeminiEmbeddingProvider(
        api_key=settings.gemini_api_key,
        # Uses the default model, but can be extracted to config later
    )
