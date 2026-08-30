"""
backend/app/core/config.py
ERP-002 FIX: SECRET_KEY now REQUIRED from environment. App refuses to start
if not set. No auto-generation, no fallback.
"""
from typing import List, Optional, Any
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "TOP WorX"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production
    SERVER_HOST: str = "http://localhost:8000"

    # ── CORS ─────────────────────────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # ── Security ─────────────────────────────────────────────────────────────
    # REQUIRED — no default, no fallback, app dies without it
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # unified name (was EMAIL_RESET_TOKEN_EXPIRE_HOURS in original,
    # PASSWORD_RESET_TOKEN_EXPIRE_HOURS in generated — keeping both as aliases)
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 2
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 2  # alias for forward-compat

    # ── Database ─────────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI: Optional[str] = None  # sync (Alembic / SQLAlchemy)

    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "topworx"
    POSTGRES_PASSWORD: str  # REQUIRED — no default
    POSTGRES_DB: str = "topworx_db"
    POSTGRES_PORT: int = 5432

    # ── Connection Pool ─────────────────────────────────────────────────────
    ASYNC_POOL_SIZE: int = 20         # Base connections in pool
    ASYNC_MAX_OVERFLOW: int = 30      # Extra connections above pool_size
    ASYNC_POOL_TIMEOUT: int = 30      # Seconds to wait for a connection
    ASYNC_POOL_RECYCLE: int = 1800    # Recycle connections after 30 min

    @property
    def DATABASE_URL(self) -> str:
        """Async URL for asyncpg (used by async SQLAlchemy sessions)."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None  # REQUIRED in production

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # ── Celery ────────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://redis:6379/0"

    # ── OpenAI ────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None

    # ── AI Configuration ─────────────────────────────────────────────────────
    AI_MODEL: str = "gpt-4o"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 4000
    AI_RATE_LIMIT_PER_MINUTE: int = 60
    AI_COST_LIMIT_PER_MONTH: float = 100.00  # USD
    AI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    AI_EMBEDDING_DIMENSIONS: int = 3072

    # ── Anthropic (optional) ─────────────────────────────────────────────────
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    # ── File Upload ───────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    # ── Email ─────────────────────────────────────────────────────────────────
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # ── i18n ──────────────────────────────────────────────────────────────────
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = ["en", "fa"]

    # ── Validators ────────────────────────────────────────────────────────────
    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters. "
                'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        if v in ("your-secret-key-here", "dev-secret-key", "changeme", "secret"):
            raise ValueError(
                "SECRET_KEY is set to a known insecure placeholder. "
                "Set a real random value in your .env file."
            )
        return v

    @field_validator("ENVIRONMENT")
    @classmethod
    def environment_must_be_valid(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @field_validator("EMAILS_FROM_NAME", mode="before")
    @classmethod
    def set_emails_from_name(cls, v: Optional[str], info: Any) -> str:
        return v or "TOP WorX"

    @field_validator("EMAILS_FROM_EMAIL", mode="before")
    @classmethod
    def set_emails_from_email(cls, v: Optional[str], info: Any) -> Optional[str]:
        return v or None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        user = data.get("POSTGRES_USER", "topworx")
        password = data.get("POSTGRES_PASSWORD", "")
        server = data.get("POSTGRES_SERVER", "postgres")
        port = data.get("POSTGRES_PORT", 5432)
        db = data.get("POSTGRES_DB", "topworx_db")
        return f"postgresql://{user}:{password}@{server}:{port}/{db}"

    @model_validator(mode="after")
    def production_checks(self) -> "Settings":
        if self.ENVIRONMENT == "production":
            if not self.REDIS_PASSWORD:
                raise ValueError("REDIS_PASSWORD is required in production")
            if self.ACCESS_TOKEN_EXPIRE_MINUTES > 60:
                raise ValueError(
                    "ACCESS_TOKEN_EXPIRE_MINUTES should be ≤ 60 in production"
                )
        return self

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# Module-level singleton — startup fails immediately if required vars are missing
settings = Settings()
