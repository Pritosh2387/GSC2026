"""
models/media_model.py — Pydantic schemas for media registration and watermarking.
"""

from pydantic import BaseModel, Field
from typing import Optional


class MediaRegisterResponse(BaseModel):
    """Returned after POST /api/media/register."""
    status: str
    content_name: str
    media_type: str
    fingerprint_dim: int
    media_id: Optional[str] = None


class WatermarkRequest(BaseModel):
    """Body for POST /api/media/watermark (non-file fields)."""
    user_id: str = Field(..., example="user_abc123")
    device_id: str = Field(..., example="device_xyz789")
    tier: str = Field("standard", example="premium")
    region: str = Field("IN", example="IN")
    content_name: str = Field("untitled", example="Champions_League_Final")


class WatermarkResponse(BaseModel):
    """Returned after watermark embedding."""
    status: str
    content_name: str
    watermark_applied: bool
    message: str
