"""AI provider abstraction layer.

Exposes the provider-agnostic `AIProvider` interface and its shared data types.
Concrete providers (Gemini today; OpenAI/Claude/Ollama later) live alongside
`base.py` and are re-exported here so callers import from a single, stable path:

    from app.services.ai import AIProvider, GeminiProvider

No provider is instantiated at import time — wiring happens at the composition
root during the integration milestone.
"""

from app.services.ai.base import (
    AIGenerationError,
    AIProvider,
    AIProviderError,
    AIProviderUnavailableError,
    GenerationResult,
    ProviderHealth,
)
from app.services.ai.factory import get_ai_provider
from app.services.ai.gemini import GeminiProvider

__all__ = [
    "AIGenerationError",
    "AIProvider",
    "AIProviderError",
    "AIProviderUnavailableError",
    "GeminiProvider",
    "GenerationResult",
    "ProviderHealth",
    "get_ai_provider",
]
