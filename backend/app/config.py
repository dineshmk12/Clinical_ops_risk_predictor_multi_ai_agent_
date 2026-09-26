from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_REPO_ROOT / ".env"), extra="ignore")

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-5"
    database_url: str = f"sqlite:///{_BACKEND_DIR / 'clinical_platform.db'}"
    high_risk_threshold: float = 0.85
    short_term_memory_ttl_hours: int = 24
    long_term_memory_retention_years: int = 7


settings = Settings()
