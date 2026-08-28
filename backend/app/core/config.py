import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "naccer-rd-evaluation-backend"
    VERSION: str = "1.0.0-p0.1"
    API_V1_PREFIX: str = "/api/v1"
    APP_ENV: str = "development"

    # Database Configuration (PostgreSQL by default, flexible for SQLite in tests)
    DATABASE_URL: str = "sqlite:///./naccer_dev.db"

    # CORS Origins Configuration
    CORS_ORIGINS: list[str] | str = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # AI & RAG Configuration (Phase P0.8)
    AI_PROVIDER: str = "deterministic"
    AI_MODEL: str = "gemini-2.5-flash"
    AI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    AI_TEMPERATURE: float = 0.2
    AI_MAX_TOKENS: int = 2048
    RAG_TOP_K_HISTORICAL: int = 5

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        try:
            return json.loads(v)
        except (json.JSONDecodeError, TypeError, ValueError):
            return ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()
