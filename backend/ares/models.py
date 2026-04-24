from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime

class Platform(str, Enum):
    YOUTUBE = "youtube"
    META = "meta"
    TIKTOK = "tiktok"
    X = "x"

class EnforcementCategory(str, Enum):
    TAKEDOWN = "takedown"
    MONETIZE = "monetize"
    LICENSE = "license"
    MONITOR = "monitor"
    HUMAN_REVIEW = "human_review"

class MatchMetadata(BaseModel):
    match_id: str
    content_id: str
    match_confidence: float = Field(..., ge=0, le=1)
    transformation_index: float = Field(..., ge=0, le=1)  # 1.0 = exact copy, 0 = unrecognizable
    view_velocity: float  # views per hour
    platform: Platform
    uploader_id: str
    uploader_reputation: float = Field(default=1.0, ge=0, le=1) # 1.0 = clean, 0 = banned history
    jurisdiction: str
    is_commercial: bool

class EnforcementAction(BaseModel):
    action_id: str
    match_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    category: EnforcementCategory
    severity_score: float
    platform_response: Dict
    blockchain_hash: Optional[str] = None
    previous_block_hash: Optional[str] = None
