"""
models/alert_model.py — Pydantic schemas for alerts and enforcement endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AlertPayload(BaseModel):
    """
    Request body for POST /api/enforcement/raw-alert.
    Also used internally when the Telegram monitor stores a piracy match.
    """
    type: str = "piracy_match"
    channel_name: Optional[str] = None
    message_id: Optional[int] = None
    similarity_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    matched_content: Optional[str] = None
    media_path: Optional[str] = None
    timestamp: Optional[str] = None
    severity: Optional[str] = "medium"
    resolved: bool = False

    model_config = {"json_schema_extra": {"example": {
        "type": "piracy_match",
        "channel_name": "@piracy_hub",
        "message_id": 12345,
        "similarity_score": 0.97,
        "matched_content": "Champions_League_Final",
        "severity": "high",
        "resolved": False,
    }}}


class AlertResponse(BaseModel):
    status: str
    alert_id: str


class EnforcementActionRequest(BaseModel):
    """
    Input for the ARES enforcement engine via POST /api/enforcement/alert.
    Wraps the ARES MatchMetadata fields.
    """
    match_id: str = "MANUAL_001"
    content_id: str = "UNKNOWN_CONTENT"
    match_confidence: float = Field(0.9, ge=0.0, le=1.0)
    transformation_index: float = Field(0.8, ge=0.0, le=1.0)
    view_velocity: float = Field(500.0, description="Estimated views/hour")
    platform: str = "youtube"
    uploader_id: str = "unknown"
    uploader_reputation: float = Field(1.0, ge=0.0, le=1.0)
    jurisdiction: str = "IN"
    is_commercial: bool = False

    model_config = {"json_schema_extra": {"example": {
        "match_id": "MATCH_001",
        "content_id": "Champions_League_Final_2026",
        "match_confidence": 0.97,
        "transformation_index": 0.85,
        "view_velocity": 1200.0,
        "platform": "youtube",
        "uploader_id": "pirate_user_99",
        "uploader_reputation": 0.1,
        "jurisdiction": "IN",
        "is_commercial": True,
    }}}
