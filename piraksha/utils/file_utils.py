"""
utils/file_utils.py — File-handling helpers for PIRAKSHA API.
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Tuple

from fastapi import UploadFile


async def save_upload_to_temp(file: UploadFile, suffix: Optional[str] = None) -> str:
    """
    Save an uploaded FastAPI UploadFile to a system temp file.
    Returns the absolute path to the temp file.
    The caller is responsible for deleting it (use cleanup_temp).
    """
    if suffix is None:
        suffix = os.path.splitext(file.filename or ".bin")[1] or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        return tmp.name


def cleanup_temp(path: str) -> None:
    """Remove a temporary file silently."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def ensure_dir(directory: str) -> str:
    """Create directory and all parents if they don't exist.  Returns the path."""
    os.makedirs(directory, exist_ok=True)
    return directory


def get_file_extension(filename: str) -> str:
    """Return lowercase extension including the dot, e.g. '.mp4'."""
    return os.path.splitext(filename)[1].lower()


def unique_filename(prefix: str = "", suffix: str = "") -> str:
    """Generate a unique filename component using UUID4."""
    return f"{prefix}{uuid.uuid4().hex}{suffix}"
