"""
database.py — Async MongoDB connection for PIRAKSHA API.

Uses Motor (async driver) for full FastAPI compatibility.

Collections used:
  users, media, fingerprints, detections, alerts, evidence, analytics
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from config import settings

# ── Module-level globals ──────────────────────────────────────────────────────
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """
    Open the MongoDB connection and create all required indexes.
    Called once at application startup.
    """
    global _client, _db
    try:
        _client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        _db = _client[settings.MONGODB_DB_NAME]

        # Verify connectivity
        await _client.admin.command("ping")
        print(f"[DB] Connected → {settings.MONGODB_DB_NAME} @ {settings.MONGODB_URI[:40]}...")

        # ── Create indexes ────────────────────────────────────────────────────
        await _db.users.create_index("email", unique=True)

        await _db.media.create_index([("registered_at", -1)])
        await _db.media.create_index("media_type")
        await _db.media.create_index("registered_by")

        await _db.fingerprints.create_index([("registered_at", -1)])
        await _db.fingerprints.create_index("media_type")
        await _db.fingerprints.create_index("content_name")

        await _db.detections.create_index([("detected_at", -1)])
        await _db.detections.create_index("similarity_score")
        await _db.detections.create_index("file_hash", unique=True, sparse=True)

        await _db.alerts.create_index([("created_at", -1)])
        await _db.alerts.create_index("severity")
        await _db.alerts.create_index("resolved")

        await _db.evidence.create_index([("logged_at", -1)])
        await _db.evidence.create_index("action_id")

        await _db.analytics.create_index([("generated_at", -1)])

        print("[DB] Indexes created / verified.")
    except Exception as exc:
        print(f"[DB] Connection failed: {exc}")
        print("[DB] Falling back — some features will be limited.")


async def close_mongo() -> None:
    """Close the MongoDB connection gracefully at shutdown."""
    global _client
    if _client:
        _client.close()
        print("[DB] MongoDB connection closed.")


def get_db() -> Optional[AsyncIOMotorDatabase]:
    """Return the active database instance (None if not connected)."""
    return _db


def is_connected() -> bool:
    """Return True when a live database handle is available."""
    return _db is not None
