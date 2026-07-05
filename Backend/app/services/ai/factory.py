from app.config import get_settings
from app.services.ai.base import AIProvider, AIProviderUnavailableError


def get_ai_provider() -> AIProvider:
    """Resolve and return the active AI provider based on configuration.

    This factory is the single composition root for selecting which AI provider
    to use (e.g., Gemini, OpenAI, Claude, Ollama). It reads the application
    settings and returns the appropriate initialized provider.

    Returns:
        An instance implementing AIProvider.

    Raises:
        AIProviderUnavailableError: If no AI provider is configured or integrated.
    """
    settings = get_settings()

    if settings.gemini_configured:
        from app.services.ai.gemini_chat import GeminiProvider

        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    raise AIProviderUnavailableError("No AI provider is configured. Please provide an API key.")
