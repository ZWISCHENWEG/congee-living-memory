import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

os.environ["GEMINI_API_KEY"] = "alias_value"
os.environ["CHRONOS_GEMINI_API_KEY"] = "prefix_value"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CHRONOS_")
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")

s = Settings()
print("Key loaded:", s.gemini_api_key)
