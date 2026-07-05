"""Gemini AI provider implementation.

Provides the concrete integration with Google's Gemini models using the
official `google-genai` SDK. This class encapsulates all vendor-specific
details, meaning callers only interact with the `AIProvider` contract.
"""

from typing import Any

from google import genai
from google.genai import errors

from app.services.ai.base import (
    AIGenerationError,
    AIProvider,
    AIProviderUnavailableError,
    GenerationResult,
    ProviderHealth,
)


class GeminiProvider(AIProvider):
    """Google Gemini implementation of `AIProvider`."""

    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        """Initialize the Gemini client.

        Args:
            api_key: Gemini API key (injected from configuration/factory).
            model: Target Gemini model identifier.

        Raises:
            AIProviderUnavailableError: If the SDK client fails to initialize.
        """
        self._model = model
        try:
            self._client = genai.Client(api_key=api_key)
        except Exception as e:
            raise AIProviderUnavailableError(f"Failed to initialize Gemini client: {e}") from e

    async def generate(self, prompt: str) -> GenerationResult:
        """Generate a completion via Gemini.

        Calls the asynchronous `generate_content` endpoint and normalizes the
        response into a `GenerationResult`. All SDK exceptions are wrapped.

        Args:
            prompt: The full text prompt to send to the model.

        Returns:
            A normalized GenerationResult object.

        Raises:
            AIGenerationError: On API failures (e.g. rate limits, bad requests).
        """
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
            )

            # Ensure the raw payload is fully JSON-serializable using Pydantic's json mode
            raw_payload: dict[str, Any] = (
                response.model_dump(mode="json") if hasattr(response, "model_dump") else {}
            )

            # response.text can be None if the generation was blocked (e.g., safety filters)
            text_result = response.text
            if text_result is None:
                text_result = ""

            return GenerationResult(
                text=text_result,
                model=self._model,
                provider=self.name,
                raw=raw_payload,
            )
        except errors.APIError as e:
            raise AIGenerationError(f"Gemini API error during generation: {e}") from e
        except Exception as e:
            raise AIGenerationError(f"Unexpected error during Gemini generation: {e}") from e

    async def health(self) -> ProviderHealth:
        """Report Gemini reachability / configuration status.

        Uses the `models.get` endpoint for the configured model as a lightweight
        network/auth probe to ensure the client can reach Google's servers.

        Returns:
            A ProviderHealth object indicating status.
        """
        try:
            await self._client.aio.models.get(model=self._model)
            return ProviderHealth(healthy=True, provider=self.name, detail="Connected")
        except errors.APIError as e:
            return ProviderHealth(healthy=False, provider=self.name, detail=f"API Error: {e}")
        except Exception as e:
            return ProviderHealth(
                healthy=False, provider=self.name, detail=f"Unexpected Error: {e}"
            )
