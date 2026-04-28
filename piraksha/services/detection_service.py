"""
services/detection_service.py — Run piracy detection on uploaded media.

Combines fingerprint generation with reference-DB comparison and persists
each result to the MongoDB 'detections' collection.
"""

from datetime import datetime, timezone
from typing import Optional

from config import settings
from database import get_db
from utils.logging_utils import get_logger
from services.fingerprint_service import generate_fingerprint, compare_against_db

logger = get_logger("piraksha.detection_service")


async def run_detection(
    file_path: str,
    threshold: float = None,
    user_id: str = "system",
) -> dict:
    """
    Full detection pipeline for a single media file.

    Steps:
      1. Generate fingerprint
      2. Compare against reference DB
      3. Persist result to MongoDB
      4. Return structured result

    Returns a dict with keys: status, media_type, fingerprint_dim, matches_found, matches
    """
    threshold = threshold or settings.SIMILARITY_THRESHOLD

    fp, media_type = generate_fingerprint(file_path)
    if fp is None or media_type is None:
        return {
            "status": "error",
            "media_type": None,
            "fingerprint_dim": 0,
            "matches_found": 0,
            "matches": [],
            "error": "Fingerprinting failed — unsupported or corrupt file",
        }

    matches = compare_against_db(fp, media_type, threshold=threshold)

    # Persist to MongoDB
    db = get_db()
    if db is not None:
        detection_doc = {
            "file_path": file_path,
            "media_type": media_type,
            "fingerprint_dim": len(fp),
            "matches_found": len(matches),
            "matches": matches,
            "threshold_used": threshold,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "detected_by": user_id,
        }
        await db.detections.insert_one(detection_doc)
        logger.info(f"Detection stored: {len(matches)} match(es)")

    return {
        "status": "ok",
        "media_type": media_type,
        "fingerprint_dim": len(fp),
        "matches_found": len(matches),
        "matches": matches,
    }


async def get_detection_results(limit: int = 50, skip: int = 0) -> list:
    """Retrieve stored detection results from MongoDB."""
    db = get_db()
    if db is None:
        return []

    cursor = db.detections.find().sort("detected_at", -1).skip(skip).limit(limit)
    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        docs.append(doc)
    return docs
