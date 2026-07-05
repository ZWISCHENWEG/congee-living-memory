"""Abstract AI provider interface.

This module defines the provider-agnostic contract that every concrete LLM
integration (Gemini, OpenAI, Claude, Ollama, ...) must implement. Routes and
services depend only on this interface, never on a specific vendor SDK, so
providers can be swapped without touching business logic.

Import the interface and its data types via:
    from app.services.ai import AIProvider, GenerationResult, ProviderHealth
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict


class AIProviderError(Exception):
    """Base class for all AI-provider failures.

    Concrete providers MUST wrap vendor-specific SDK exceptions in one of these
    so callers can handle failures without importing any vendor SDK. This is the
    error half of the swap-any-provider contract.
    """


class AIGenerationError(AIProviderError):
    """A `generate` call failed (bad request, model error, timeout, ...)."""


class AIProviderUnavailableError(AIProviderError):
    """The provider is unreachable or misconfigured (auth, network, quota)."""


class GenerationResult(BaseModel):
    """Normalized output of a single `generate` call.

    Every provider maps its raw SDK response onto this shape so that callers
    receive a stable, vendor-neutral result regardless of the backend used.
    Immutable: it is a value object returned to callers, not a mutable buffer.
    """

    model_config = ConfigDict(frozen=True)

    text: str
    model: str
    provider: str
    # Raw provider payload for debugging / future features (token usage, etc.).
    raw: dict[str, Any] | None = None


class ProviderHealth(BaseModel):
    """Normalized result of a provider health probe (immutable value object)."""

    model_config = ConfigDict(frozen=True)

    healthy: bool
    provider: str
    detail: str | None = None


class AIProvider(ABC):
    """Provider-agnostic interface for text generation backends.

    Concrete providers subclass this and implement `generate` and `health`.
    Keeping the surface area small keeps every provider easy to reason about
    and trivial to swap at the composition root.
    """

    #: Stable, human-readable provider identifier (e.g. "gemini", "openai").
    name: str = "base"

    @abstractmethod
    async def generate(self, prompt: str) -> GenerationResult:
        """Generate a completion for `prompt`.

        Args:
            prompt: The fully-assembled prompt to send to the model.

        Returns:
            A `GenerationResult` with the generated text and metadata.

        Raises:
            NotImplementedError: If the concrete provider is not yet wired up.
        """
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> ProviderHealth:
        """Report whether the provider is reachable and correctly configured.

        Returns:
            A `ProviderHealth` describing the current provider status.
        """
        raise NotImplementedError
