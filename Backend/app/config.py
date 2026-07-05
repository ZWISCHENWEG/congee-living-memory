"""Application configuration.

Settings are loaded from environment variables (and an optional `.env` file)
using Pydantic v2's `BaseSettings`. Import the shared `settings` singleton via
`from app.config import settings`.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings sourced from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CHRONOS_",
        extra="ignore",
    )

    # --- Application metadata ---
    project_name: str = "Chronos"
    version: str = "0.1.0"
    debug: bool = False

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- Database ---
    # SQLite file path (relative paths resolve against the backend working dir).
    database_url: str = "sqlite:///./chronos.db"

    # --- CORS ---
    # Comma-separated origins allowed by the frontend during development.
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # --- AI providers: Gemini ---
    # Optional. Kept unset by default so the app boots without Gemini wired up
    # (the provider is not integrated yet). No key is hardcoded; only the model
    # name carries a sensible default. Read from the standard, unprefixed
    # `GEMINI_*` names (the explicit alias bypasses the `CHRONOS_` env prefix).
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", validation_alias="GEMINI_MODEL")

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS origins as a clean list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def gemini_configured(self) -> bool:
        """Whether a Gemini API key is present.

        Lets the future composition root decide whether to wire up the Gemini
        provider — without importing any SDK or making a network call here.
        """
        return bool(self.gemini_api_key)


@lru_cache
def get_settings() -> Settings:
    """Return a cached `Settings` instance."""
    return Settings()


settings = get_settings()
