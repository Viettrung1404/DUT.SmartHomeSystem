from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ai_server_port: int = 8100
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5433/smarthome"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    ai_server_api_key: str = "change_me"
    memory_backend: str = "memory"
    request_timeout_seconds: int = 60
    max_tool_rows: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

