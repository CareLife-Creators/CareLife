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

    database_url: SecretStr = Field(min_length=1)
    secret_key: SecretStr = Field(min_length=32)

    access_token_expire_minutes: int = Field(default=30, gt=0)
    license_expiry_reminder_days: int = Field(default=30, gt=0)

    reset_token_expire_minutes: int = Field(default=30, gt=0)

    reset_link_base_url: str = "http://localhost:3000/reset-password"

    email_mode: Literal["console", "smtp"] = "console"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    email_from: str = "no-reply@carelife.local"

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

    @property
    def smtp_password_value(self) -> str | None:
        if self.smtp_password is None:
            return None

        return self.smtp_password.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()