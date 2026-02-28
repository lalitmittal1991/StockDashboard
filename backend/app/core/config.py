"""Application configuration."""
from pathlib import Path

from pydantic_settings import BaseSettings
from functools import lru_cache

# .env is in backend/ - resolve path relative to this file
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # App
    APP_NAME: str = "Stock Dashboard"
    DEBUG: bool = False

    # Auth - single allowed user (no registration)
    ALLOWED_USERNAME: str = ""
    ALLOWED_PASSWORD: str = ""
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Google Sheets - use service account JSON path or OAuth
    GOOGLE_SHEETS_CREDENTIALS_PATH: str = "credentials.json"
    # Or use base64 encoded JSON for Cloud Run
    GOOGLE_SHEETS_CREDENTIALS_JSON: str | None = None

    # GNews API - get free key at https://gnews.io/ (news source)
    GNEWS_API_KEY: str = ""

    # Google Gemini API - for summarization & analysis (get key at https://aistudio.google.com/apikey)
    GEMINI_API_KEY: str = ""

    # YouTube Data API - get from Google Cloud Console
    YOUTUBE_API_KEY: str = ""

    # Database - use /tmp for Cloud Run (ephemeral) or ./ for local
    DATABASE_URL: str = "sqlite+aiosqlite:///./stock_dashboard.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = str(_ENV_FILE) if _ENV_FILE.exists() else ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
