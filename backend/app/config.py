"""Application configuration.

All config is driven by environment variables. Secrets must never be
hard-coded. ``DATABASE_URL`` allows switching between MySQL (production)
and SQLite (local development fallback).
"""

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _origins():
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [o.strip() for o in raw.split(",") if o.strip()]


class BaseConfig:
    """Defaults shared by every environment."""

    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "720"))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    CORS_ORIGINS = _origins()

    AI_PROVIDER = os.getenv("AI_PROVIDER", "demo")
    AI_API_KEY = os.getenv("AI_API_KEY", "")

    RATE_LIMIT_ENABLED = _env_bool("RATE_LIMIT_ENABLED", False)


class DevelopmentConfig(BaseConfig):
    """Local development. Uses SQLite unless DATABASE_URL is provided."""

    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "ayuconnect_dev.db")
    )


class TestingConfig(BaseConfig):
    """Automated tests. In-memory SQLite by default."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production. Requires explicit secrets; debug is always off."""

    DEBUG = False

    def __init__(self):
        # Read at instantiation so tests can override environment variables,
        # and so a missing secret fails fast here rather than later.
        self.SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "")
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")

        if not self.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError("DATABASE_URL must be set in production")
        if self.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
            raise RuntimeError("SQLite is not allowed in production. Use MySQL.")
        if self.SECRET_KEY in (None, "", "dev-only-secret"):
            raise RuntimeError("SECRET_KEY must be set in production")
        if self.JWT_SECRET_KEY in (None, "", "dev-only-secret"):
            raise RuntimeError("JWT_SECRET_KEY must be set in production")


_CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name=None):
    """Return an instantiated config for ``name`` (default: FLASK_ENV).

    Instantiation triggers ProductionConfig validation, which fails fast
    when required production settings are missing.
    """
    name = (name or os.getenv("FLASK_ENV", "development")).strip().lower()
    if name not in _CONFIGS:
        raise ValueError(f"Unknown configuration '{name}'")
    return _CONFIGS[name]()