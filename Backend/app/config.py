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

    # --- Search ---
    search_limit: int = 10
    similarity_threshold: float = 0.65

    # --- Phase 3: autonomous memory engine ---
    # Similarity at/above which a candidate save is treated as a duplicate.
    duplicate_threshold: float = 0.92
    # Similarity band that flags a potential conflict/update (below duplicate).
    conflict_threshold: float = 0.75
    # Gemini confidence required to auto-replace on a detected conflict.
    conflict_confidence: float = 0.90
    # Similarity required to match a "forget X" request to a stored memory.
    forget_threshold: float = 0.80
    # Composite ranking weights (Feature 11). Should sum to 1.0.
    rank_weight_similarity: float = 0.60
    rank_weight_importance: float = 0.20
    rank_weight_recency: float = 0.10
    rank_weight_usage: float = 0.10

    # --- AI providers: Gemini ---
    # The key is optional so the app still boots without it: the AI/embedding
    # factories fall back to unavailable/null providers and chat degrades
    # gracefully instead of crashing. No key is hardcoded; only the model name
    # carries a sensible default. Read from the standard, unprefixed `GEMINI_*`
    # names (the explicit alias bypasses the `CHRONOS_` env prefix).
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
