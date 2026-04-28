"""
config.py — PIRAKSHA API configuration.

Reads all environment variables from the project-root .env file and exposes
them as a single Settings object consumed throughout the application.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ── Locate the project root (.env lives one level above piraksha/) ────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)

# ── Add the backend directory to sys.path so existing modules are importable ──
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# ── Application settings ──────────────────────────────────────────────────────

class Settings:
    """Central settings object.  All values fall back to safe defaults."""

    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "sportguard")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET_KEY", os.getenv("JWT_SECRET", "piraksha-secret-change-me"))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Telegram
    TELEGRAM_API_ID: str = os.getenv("TELEGRAM_API_ID", "")
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")

    # Paths
    PROJECT_ROOT: Path = PROJECT_ROOT
    BACKEND_DIR: Path = BACKEND_DIR
    MEDIA_DOWNLOADS_DIR: Path = BACKEND_DIR / "media_downloads"
    REFERENCE_FP_JSON: Path = BACKEND_DIR / "reference_fingerprints.json"
    MATCHES_JSON: Path = BACKEND_DIR / "telegram_matches.json"
    ALERTS_JSON: Path = BACKEND_DIR / "telegram_alerts.json"
    LEDGER_JSON: Path = PROJECT_ROOT / "ares_ledger.json"
    SESSION_PATH: str = str(BACKEND_DIR / "session")

    # Fingerprint similarity threshold
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.9"))

    # CORS — origins allowed to talk to this API
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",  # widen for hackathon demo; restrict in production
    ]

    # API metadata
    API_TITLE: str = "PIRAKSHA API"
    API_DESCRIPTION: str = (
        "PIRAKSHA — AI-Powered Media Piracy Detection System. "
        "Unified backend exposing fingerprinting, watermarking, Telegram monitoring, "
        "deepfake detection, network tracing, enforcement, and analytics."
    )
    API_VERSION: str = "2.0.0"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"


settings = Settings()
