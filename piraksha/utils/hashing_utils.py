"""
utils/hashing_utils.py — Cryptographic helpers for PIRAKSHA API.
"""

import hashlib


def sha256_file(file_path: str) -> str:
    """Compute SHA-256 hash of a file (chunk-reads for large files)."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_string(data: str) -> str:
    """Compute SHA-256 hash of a UTF-8 string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of raw bytes."""
    return hashlib.sha256(data).hexdigest()
