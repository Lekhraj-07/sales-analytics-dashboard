"""Centralized logging configuration."""
import logging
import sys
from typing import Optional


_configured = False


def get_logger(name: str = "analytics", level: str = "INFO",
                fmt: Optional[str] = None) -> logging.Logger:
    """Return a configured logger. Idempotent."""
    global _configured
    logger = logging.getLogger(name)
    if not _configured:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            fmt or "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        root = logging.getLogger()
        root.handlers.clear()
        root.addHandler(handler)
        root.setLevel(getattr(logging, level.upper(), logging.INFO))
        _configured = True
    return logger
