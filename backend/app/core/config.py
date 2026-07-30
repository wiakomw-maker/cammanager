from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://cammanager:change-me@db:5432/cammanager"
    hikvision_verify_tls: bool = False
    hikvision_request_timeout_seconds: float = 10.0
    credentials_encryption_key: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
