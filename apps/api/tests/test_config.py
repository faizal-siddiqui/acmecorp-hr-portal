"""
TDD: settings load from defaults and environment variables.
"""

import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from app.config import Settings


class IsolatedSettings(Settings):
    """Settings without .env file loading — isolates tests from the filesystem."""

    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )


def test_settings_defaults() -> None:
    settings = IsolatedSettings()
    assert settings.database_url == "sqlite+aiosqlite:///./salary.db"
    assert settings.secret_key == "change-me-in-production"
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes == 480
    assert settings.cors_origins == ["http://localhost:3000"]
    assert settings.environment == "development"
    assert settings.debug is False


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@db:5432/salary")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,https://app.example.com")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "true")

    settings = IsolatedSettings()

    assert settings.database_url == "postgresql+asyncpg://user:pass@db:5432/salary"
    assert settings.secret_key == "test-secret"
    assert settings.cors_origins == ["http://localhost:3000", "https://app.example.com"]
    assert settings.environment == "test"
    assert settings.debug is True


def test_cors_origins_parses_comma_separated_string() -> None:
    settings = IsolatedSettings.model_validate(
        {"cors_origins": "http://a.test, http://b.test"},
    )
    assert settings.cors_origins == ["http://a.test", "http://b.test"]


def test_cors_origins_accepts_list() -> None:
    origins = ["http://localhost:3000", "http://localhost:3001"]
    settings = IsolatedSettings(cors_origins=origins)
    assert settings.cors_origins == origins


def test_debug_rejects_invalid_boolean(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "not-a-bool")
    with pytest.raises(ValidationError):
        IsolatedSettings()
