from app.config import get_settings
from app.services.embedding.base import EmbeddingProvider, EmbeddingProviderUnavailableError
from app.services.embedding.gemini import GeminiEmbeddingProvider


class NullEmbeddingProvider(EmbeddingProvider):
    """Null object pattern for when no provider is configured."""

    @property
    def name(self) -> str:
        return "unconfigured_provider"

    async def generate_embedding(self, text: str) -> list[float]:
        raise EmbeddingProviderUnavailableError("Embedding provider is not configured.")


def get_embedding_provider() -> EmbeddingProvider:
    """Factory to instantiate and return the configured Embedding Provider."""
    settings = get_settings()

    if not settings.gemini_configured:
        return NullEmbeddingProvider()

    return GeminiEmbeddingProvider(
        api_key=settings.gemini_api_key,
    )
