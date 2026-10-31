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
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5180",
        "http://127.0.0.1:5180",
    ]

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

    # bKash Checkout configuration. Credentials belong in backend/.env.
    bkash_api_base_url: str = (
        "https://tokenized.sandbox.bka.sh/v2/tokenized-checkout"
    )
    bkash_username: str | None = None
    bkash_password: SecretStr | None = None
    bkash_app_key: SecretStr | None = None
    bkash_app_secret: SecretStr | None = None
    bkash_callback_url: str = (
        "http://localhost:8000/donations/bkash/callback"
    )

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
