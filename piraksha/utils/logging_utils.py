"""
utils/logging_utils.py — Structured logging for PIRAKSHA API.

Sets up a consistent log format used across all services and routes.
"""

import logging
import sys
from pathlib import Path

from config import settings

# ── Formatter ────────────────────────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s"
LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"

_LOG_FILE = settings.PROJECT_ROOT / "piraksha_api.log"


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger configured with both console and file handlers.
    Repeated calls with the same name return the same logger (standard Python behaviour).
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured; avoid adding duplicate handlers
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FMT)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    try:
        fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except OSError:
        pass  # If we can't write a log file, console output is still available

    return logger
