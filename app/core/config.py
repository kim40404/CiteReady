"""CiteReady application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env file or environment."""

    # App identity
    APP_NAME: str = "CiteReady"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "AI Search Visibility Scoring Engine — Know if AI will cite your content."

    # Logging
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/citeready.db"

    # CORS Config
    FRONTEND_CORS_ORIGINS: str = "*"  # Comma-separated list for production, e.g., "https://citeready.com"

    # AI Provider Settings (Supports local Ollama or Cloud Providers via LiteLLM)
    LLM_PROVIDER: str = "ollama"  # e.g., 'ollama', 'openai', 'anthropic'
    LLM_MODEL: str = "ollama/llama3.1"
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_API_KEY: str | None = None
    LLM_TIMEOUT: int = 45  # Adjust for production APIs

    # Scraper settings
    SCRAPER_TIMEOUT: int = 15  # seconds
    SCRAPER_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    )

    # Scoring thresholds
    MIN_WORD_COUNT: int = 300
    IDEAL_WORD_COUNT: int = 1500

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
