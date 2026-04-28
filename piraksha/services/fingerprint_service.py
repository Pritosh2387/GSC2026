"""
services/fingerprint_service.py — Fingerprint generation and comparison.

Wraps the existing SportGuard fingerprinting engine and ReferenceDatabase.
"""

from typing import Optional
import numpy as np

from config import settings
from utils.logging_utils import get_logger

logger = get_logger("piraksha.fingerprint_service")


def generate_fingerprint(file_path: str) -> tuple[Optional[np.ndarray], Optional[str]]:
    """
    Generate a fingerprint for the media file at *file_path*.

    Returns:
        (fingerprint_array, media_type) — both None on failure.
    """
    try:
        from telegram.telegram_utils import (
            get_media_type,
            fingerprint_image,
            fingerprint_video,
        )

        media_type = get_media_type(file_path)
        if media_type is None:
            logger.warning(f"Unsupported file type: {file_path}")
            return None, None

        logger.info(f"Generating fingerprint for {media_type}: {file_path}")
        fp = (
            fingerprint_image(file_path)
            if media_type == "image"
            else fingerprint_video(file_path)
        )

        if fp is None:
            logger.error(f"Fingerprinting returned None for {file_path}")
        return fp, media_type

    except Exception as exc:
        logger.error(f"Fingerprint generation failed: {exc}", exc_info=True)
        return None, None


def compare_against_db(fingerprint: np.ndarray, media_type: str, threshold: float = None) -> list:
    """
    Compare *fingerprint* against all registered reference fingerprints.

    Returns a list of match dicts sorted by similarity_score descending.
    """
    from telegram.telegram_utils import ReferenceDatabase

    threshold = threshold or settings.SIMILARITY_THRESHOLD
    ref_db = ReferenceDatabase(db_path=str(settings.REFERENCE_FP_JSON))
    matches = ref_db.find_matches(fingerprint, media_type, threshold=threshold)
    logger.info(f"Compared fingerprint → {len(matches)} match(es) above {threshold}")
    return matches


def register_in_reference_db(
    file_path: str,
    content_name: str,
    media_type: str,
    fingerprint: np.ndarray,
) -> None:
    """Persist the fingerprint to the JSON reference database."""
    from telegram.telegram_utils import ReferenceDatabase

    ref_db = ReferenceDatabase(db_path=str(settings.REFERENCE_FP_JSON))
    ref_db.register(file_path, content_name, media_type, fingerprint)
    logger.info(f"Registered '{content_name}' in reference DB ({media_type}, {len(fingerprint)}-dim)")
