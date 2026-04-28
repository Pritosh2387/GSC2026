"""
services/enforcement_service.py — Enforcement action pipeline.

Wraps the ARES DecisionEngine + AresOrchestrator + EvidenceLedger
and persists actions to MongoDB 'evidence' collection.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from config import settings
from database import get_db
from utils.logging_utils import get_logger

logger = get_logger("piraksha.enforcement_service")


def _oid(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def trigger_enforcement(action_data: dict, user_id: str = "system") -> dict:
    """
    Run the full ARES enforcement pipeline for a piracy match.

    Returns:
        {
          "action_id": str,
          "category": str,
          "severity_score": float,
          "ai_analysis": dict,
          "blockchain_hash": str,
        }
    """
    from ares.models import MatchMetadata, Platform
    from ares.engine import DecisionEngine, MockGeminiAdapter
    from ares.ledger import EvidenceLedger

    platform_map = {
        "youtube": Platform.YOUTUBE,
        "meta": Platform.META,
        "tiktok": Platform.TIKTOK,
        "x": Platform.X,
    }

    match = MatchMetadata(
        match_id=action_data.get("match_id", f"MATCH_{uuid.uuid4().hex[:8].upper()}"),
        content_id=action_data.get("content_id", "UNKNOWN"),
        match_confidence=float(action_data.get("match_confidence", 0.9)),
        transformation_index=float(action_data.get("transformation_index", 0.8)),
        view_velocity=float(action_data.get("view_velocity", 500.0)),
        platform=platform_map.get(
            str(action_data.get("platform", "youtube")).lower(), Platform.YOUTUBE
        ),
        uploader_id=str(action_data.get("uploader_id", "unknown")),
        uploader_reputation=float(action_data.get("uploader_reputation", 1.0)),
        jurisdiction=str(action_data.get("jurisdiction", "IN")),
        is_commercial=bool(action_data.get("is_commercial", False)),
    )

    engine = DecisionEngine(MockGeminiAdapter())
    category, score, ai_analysis = engine.classify(match)

    # Blockchain ledger entry
    ledger = EvidenceLedger(storage_path=str(settings.LEDGER_JSON))
    from ares.models import EnforcementAction
    enforcement_action = EnforcementAction(
        action_id=f"ACT_{uuid.uuid4().hex[:8].upper()}",
        match_id=match.match_id,
        category=category,
        severity_score=score,
        platform_response={"platform": match.platform.value, "status": "logged"},
    )
    block_hash = ledger.log_action(enforcement_action)

    # Persist to MongoDB
    db = get_db()
    doc = {
        "action_id": enforcement_action.action_id,
        "match_id": match.match_id,
        "content_id": match.content_id,
        "category": category.value,
        "severity_score": score,
        "ai_reasoning": ai_analysis.get("reasoning", ""),
        "ai_suggested_action": ai_analysis.get("suggested_action", ""),
        "parody_probability": ai_analysis.get("parody_probability", 0),
        "commercial_intent": ai_analysis.get("commercial_intent", ""),
        "platform": match.platform.value,
        "blockchain_hash": block_hash,
        "logged_at": datetime.now(timezone.utc).isoformat(),
        "triggered_by": user_id,
    }
    if db is not None:
        await db.evidence.insert_one(doc)

    logger.info(
        f"Enforcement: {category.value.upper()} | score={score:.3f} | "
        f"hash={block_hash[:16]}..."
    )

    return {
        "action_id": enforcement_action.action_id,
        "category": category.value,
        "severity_score": score,
        "ai_analysis": ai_analysis,
        "blockchain_hash": block_hash,
    }


async def get_enforcement_logs(limit: int = 50, skip: int = 0) -> list:
    """Retrieve enforcement history from MongoDB."""
    db = get_db()
    if db is None:
        return []
    cursor = db.evidence.find().sort("logged_at", -1).skip(skip).limit(limit)
    docs = []
    async for doc in cursor:
        docs.append(_oid(doc))
    return docs
