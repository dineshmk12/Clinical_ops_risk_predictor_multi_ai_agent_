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
    log_level: str = "INFO"

    # Risk tier boundaries (skills/risk_scoring.py) and the per-agent
    # thresholds that decide whether an event is published to the bus.
    risk_tier_critical_threshold: float = 0.7
    risk_tier_at_risk_threshold: float = 0.4
    enrollment_risk_publish_threshold: float = 0.5
    site_risk_publish_threshold: float = 0.7

    # Enrollment forecasting windows (skills/enrollment_forecasting.py), per SOP-002.
    planned_enrollment_window_weeks: int = 26
    forecast_horizon_weeks: int = 12


settings = Settings()
