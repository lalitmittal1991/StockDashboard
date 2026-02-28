"""Application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # App
    APP_NAME: str = "Stock Dashboard"
    DEBUG: bool = False

    # Auth
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Google Sheets - use service account JSON path or OAuth
    GOOGLE_SHEETS_CREDENTIALS_PATH: str = "credentials.json"
    # Or use base64 encoded JSON for Cloud Run
    GOOGLE_SHEETS_CREDENTIALS_JSON: str | None = None

    # GNews API - get free key from https://gnews.io/
    GNEWS_API_KEY: str = ""

    # YouTube Data API - get from Google Cloud Console
    YOUTUBE_API_KEY: str = ""

    # Database - use /tmp for Cloud Run (ephemeral) or ./ for local
    DATABASE_URL: str = "sqlite+aiosqlite:///./stock_dashboard.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
