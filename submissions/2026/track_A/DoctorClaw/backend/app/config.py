from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: Literal["mock", "gemma"] = "gemma"
    llm_base_url: str = "https://api.deepinfra.com/v1/openai"
    llm_api_key: str = ""
    llm_model: str = "google/gemma-4-31B-it"
    llm_timeout: float = 120.0
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.3
    llm_fallback_to_mock: bool = True
    llm_disable_thinking: bool = True
    llm_enable_thinking: bool = False
    llm_structured_output_mode: Literal["json_object", "json_schema"] = "json_schema"
    llm_stream_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
