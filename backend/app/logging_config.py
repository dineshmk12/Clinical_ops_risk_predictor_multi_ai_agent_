"""Centralized logging setup — call once at process start (main.py, seed_data.py).
Level is configurable via LOG_LEVEL (see config.py) instead of each module
wiring up its own handler."""
import logging

from app.config import settings

_configured = False


def configure_logging() -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    _configured = True
