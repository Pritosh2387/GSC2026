"""
models/detection_model.py — Pydantic schemas for detection and deepfake endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class DetectionResult(BaseModel):
    """A single fingerprint-match detection result."""
    content_name: str
    similarity_score: float
    media_type: str
    registered_at: str
    channel_name: Optional[str] = None
    message_id: Optional[int] = None


class DetectionRunResponse(BaseModel):
    """Returned after POST /api/detection/run."""
    status: str
    media_type: str
    fingerprint_dim: int
    matches_found: int
    matches: List[DetectionResult]


class DeepfakeAnalysisResponse(BaseModel):
    """Returned after POST /api/deepfake/analyze."""
    prediction: int            # 0 = real, 1 = deepfake
    probability: float         # confidence score in [0, 1]
    label: str                 # "REAL" or "DEEPFAKE"
    model_available: bool
