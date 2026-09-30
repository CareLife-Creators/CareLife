from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "CareLife API"

    environment: Literal[
        "development",
        "testing",
        "staging",
        "production",
    ] = "development"

    debug: bool = False

    # Sensitive configuration must come from the environment.
    database_url: SecretStr = Field(min_length=1)
    secret_key: SecretStr = Field(min_length=32)

    access_token_expire_minutes: int = Field(default=30, gt=0)

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url_value(self) -> str:
        return self.database_url.get_secret_value()

    @property
    def secret_key_value(self) -> str:
        return self.secret_key.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()


