"""
telegram_utils.py — Utility functions for SportGuard Telegram integration.

Provides:
  - File hashing (SHA-256) for duplicate detection
  - Media type detection (image vs video)
  - Image fingerprinting (DCT perceptual hash, 128-dim)
  - Video fingerprinting (full 512-dim via SportGuard engine)
  - Cosine-similarity comparison
  - Reference fingerprint database (JSON-backed)
  - Match result storage (JSON-backed)
  - Alert dispatch (local JSON + optional HTTP POST to backend)
"""

import os
import sys
import hashlib
import json
import logging
import numpy as np
import cv2
from datetime import datetime
from typing import Optional, Dict, List

# Ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logger = logging.getLogger("sportguard.telegram")

# Constants
SIMILARITY_THRESHOLD = 0.9
REFERENCE_DB_PATH = os.path.join(PROJECT_ROOT, "reference_fingerprints.json")
MATCHES_DB_PATH = os.path.join(PROJECT_ROOT, "telegram_matches.json")
ALERTS_DB_PATH = os.path.join(PROJECT_ROOT, "telegram_alerts.json")

SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".gif"}
SUPPORTED_VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".webm", ".flv", ".wmv", ".3gp"}

# Duplicate Detection

def compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of a file for deduplication."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

# Media Type Detection

def get_media_type(file_path: str) -> Optional[str]:
    """Return 'image', 'video', or None based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in SUPPORTED_IMAGE_EXTS:
        return "image"
    if ext in SUPPORTED_VIDEO_EXTS:
        return "video"
    return None

# Frame Extraction (for video fingerprinting)

def extract_frames_from_video(video_path: str, num_frames: int = 10) -> List[np.ndarray]:
    """Extract *num_frames* evenly-spaced frames from a video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        return []

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        return []

    indices = np.linspace(0, total - 1, num_frames, dtype=int)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames

# Image Fingerprinting  (DCT perceptual hash — same technique as
# sportguard.fingerprinting.visual but adapted for a single image)

def fingerprint_image(image_path: str) -> Optional[np.ndarray]:
    """
    Generate a **128-dim** DCT perceptual-hash fingerprint from a single
    image.  Uses the same DCT approach as the SportGuard VisualFingerprint
    so that similarity comparisons are consistent.
    """
    frame = cv2.imread(image_path)
    if frame is None:
        logger.error(f"Cannot read image: {image_path}")
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)

    # 2-D DCT → keep top-left 8×8 (mid-frequencies)
    resized = resized.astype(np.float32)
    dct = cv2.dct(resized)
    dct_low = dct[:8, :8]
    avg = dct_low.mean()
    hash_bits = (dct_low > avg).flatten().astype(np.float32)  # 64 values

    # Tile to 128-dim (matches VisualFingerprint.dimensionality)
    fingerprint = np.tile(hash_bits, 2)

    # L2 normalise
    norm = np.linalg.norm(fingerprint)
    if norm > 0:
        fingerprint /= norm
    return fingerprint

# Video Fingerprinting  (reuses existing SportGuard engine)

def fingerprint_video(video_path: str) -> Optional[np.ndarray]:
    """
    Generate a **512-dim** fused fingerprint from a video file by reusing
    the existing SportGuard FingerprintingEngine (visual + audio + temporal
    + semantic modalities).
    """
    try:
        from sportguard.fingerprinting.engine import FingerprintingEngine
        from sportguard.fingerprinting.fusion import ContentType

        engine = FingerprintingEngine()
        return engine.generate_fingerprint(video_path, ContentType.GENERAL)
    except Exception as e:
        logger.error(f"Full video fingerprinting failed ({e}), falling back to visual-only.")

    # ---- Fallback: visual-only fingerprint via frame extraction ----
    try:
        frames = extract_frames_from_video(video_path)
        if not frames:
            return None

        hashes = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
            resized = resized.astype(np.float32)
            dct = cv2.dct(resized)
            dct_low = dct[:8, :8]
            avg = dct_low.mean()
            hashes.append((dct_low > avg).flatten())

        combined = np.concatenate(hashes).astype(np.float32)
        if len(combined) > 128:
            combined = combined[:128]
        else:
            combined = np.pad(combined, (0, max(0, 128 - len(combined))))

        norm = np.linalg.norm(combined)
        if norm > 0:
            combined /= norm
        return combined
    except Exception as ex:
        logger.error(f"Fallback video fingerprinting also failed: {ex}")
        return None

# Fingerprint Comparison  (cosine similarity)

def compare_fingerprints(fp1: np.ndarray, fp2: np.ndarray) -> float:
    """
    Cosine similarity between two fingerprints.
    Returns a float in [0, 1] where 1.0 = identical.
    Vectors must share the same dimensionality.
    """
    if fp1.shape != fp2.shape:
        return 0.0
    n1, n2 = np.linalg.norm(fp1), np.linalg.norm(fp2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.clip(np.dot(fp1, fp2) / (n1 * n2), 0.0, 1.0))

# Reference Fingerprint Database  (JSON file-backed)

class ReferenceDatabase:
    """Stores registered *original* content fingerprints."""

    def __init__(self, db_path: str = REFERENCE_DB_PATH):
        self.db_path = db_path
        self.entries: List[Dict] = self._load()

    # -- persistence helpers
    def _load(self) -> List[Dict]:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def _save(self):
        with open(self.db_path, "w") as f:
            json.dump(self.entries, f, indent=2)

    # -- public API 
    def register(self, content_path: str, content_name: str,
                 media_type: str, fingerprint: np.ndarray):
        """Register a new original-content fingerprint."""
        self.entries.append({
            "content_name": content_name,
            "content_path": content_path,
            "media_type": media_type,
            "fingerprint": fingerprint.tolist(),
            "dimension": len(fingerprint),
            "registered_at": datetime.now().isoformat(),
        })
        self._save()
        logger.info(f"Registered: {content_name} ({media_type}, {len(fingerprint)}-dim)")

    def find_matches(self, fingerprint: np.ndarray, media_type: str,
                     threshold: float = SIMILARITY_THRESHOLD) -> List[Dict]:
        """Return all reference entries whose similarity ≥ *threshold*."""
        matches = []
        for entry in self.entries:
            if entry["media_type"] != media_type:
                continue
            if entry["dimension"] != len(fingerprint):
                continue
            ref_fp = np.array(entry["fingerprint"], dtype=np.float32)
            sim = compare_fingerprints(fingerprint, ref_fp)
            if sim >= threshold:
                matches.append({
                    "content_name": entry["content_name"],
                    "content_path": entry["content_path"],
                    "similarity_score": round(sim, 4),
                    "registered_at": entry["registered_at"],
                })
        matches.sort(key=lambda m: m["similarity_score"], reverse=True)
        return matches

# ---------------------------------------------------------------------------
# Match Result Storage  (JSON file-backed)
# ---------------------------------------------------------------------------

class MatchResultStore:
    """Persists Telegram piracy-match results and tracks processed files."""

    def __init__(self, db_path: str = MATCHES_DB_PATH):
        self.db_path = db_path
        self._processed_hashes: set = set()
        self._load_processed_hashes()

    def _load_processed_hashes(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    for rec in json.load(f):
                        h = rec.get("file_hash")
                        if h:
                            self._processed_hashes.add(h)
            except (json.JSONDecodeError, IOError):
                pass

    def is_duplicate(self, file_hash: str) -> bool:
        return file_hash in self._processed_hashes

    def store_match(self, *, channel_name: str, message_id: int,
                    timestamp: str, similarity_score: float,
                    media_path: str, media_type: str,
                    matched_content: str, file_hash: str) -> Dict:
        """Append a match record and return it."""
        record = {
            "channel_name": channel_name,
            "message_id": message_id,
            "timestamp": timestamp,
            "similarity_score": similarity_score,
            "media_path": media_path,
            "media_type": media_type,
            "matched_content": matched_content,
            "file_hash": file_hash,
            "detected_at": datetime.now().isoformat(),
        }

        records = []
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    records = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        records.append(record)
        self._processed_hashes.add(file_hash)
        with open(self.db_path, "w") as f:
            json.dump(records, f, indent=2)

        logger.info(
            f"Match stored: {channel_name} | msg:{message_id} "
            f"| score:{similarity_score}"
        )
        return record

# ---------------------------------------------------------------------------
# Alert Dispatch
# ---------------------------------------------------------------------------

def _store_alert_locally(alert: Dict):
    """Append an alert to the local JSON alerts file."""
    alerts = []
    if os.path.exists(ALERTS_DB_PATH):
        try:
            with open(ALERTS_DB_PATH, "r") as f:
                alerts = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    alerts.append(alert)
    with open(ALERTS_DB_PATH, "w") as f:
        json.dump(alerts, f, indent=2)


def send_alert(match_data: Dict,
               api_url: str = "http://127.0.0.1:8000/telegram-alerts"):
    """
    Build an alert payload, store it locally, and optionally POST it
    to the backend API.  Never raises — failures are logged.
    """
    alert = {
        "type": "piracy_match",
        "channel_name": match_data.get("channel_name"),
        "message_id": match_data.get("message_id"),
        "similarity_score": match_data.get("similarity_score"),
        "matched_content": match_data.get("matched_content"),
        "media_path": match_data.get("media_path"),
        "timestamp": datetime.now().isoformat(),
        "severity": (
            "HIGH" if match_data.get("similarity_score", 0) > 0.95
            else "MEDIUM"
        ),
    }

    _store_alert_locally(alert)

    try:
        import requests
        resp = requests.post(api_url, json=alert, timeout=5)
        if resp.status_code == 200:
            logger.info(f"🔔 Alert sent to API: {api_url}")
        else:
            logger.warning(f"API responded with {resp.status_code}")
    except Exception as e:
        logger.warning(f"Could not reach API ({api_url}): {e}. Alert stored locally.")

    return alert
