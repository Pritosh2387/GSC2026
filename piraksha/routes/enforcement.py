"""
routes/enforcement.py — Enforcement action endpoints.

POST /api/enforcement/alert — Trigger ARES enforcement pipeline
GET  /api/enforcement/logs  — Return enforcement history
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from auth import get_current_user
from database import get_db
from models.alert_model import AlertPayload, AlertResponse, EnforcementActionRequest
from services import enforcement_service
from utils.logging_utils import get_logger

router = APIRouter(prefix="/api/enforcement", tags=["Enforcement"])
logger = get_logger("piraksha.routes.enforcement")


@router.post(
    "/alert",
    response_model=None,
    summary="Trigger enforcement action",
    description=(
        "Submit a piracy match to the ARES enforcement engine. "
        "ARES calculates an Action Severity Score, classifies the infringement "
        "(TAKEDOWN / MONETIZE / LICENSE / MONITOR), logs the decision to a "
        "blockchain-style evidence ledger, and stores the result in MongoDB."
    ),
)
async def trigger_alert(
    data: EnforcementActionRequest,
    current=Depends(get_current_user),
):
    """
    **Trigger** the full ARES enforcement pipeline for a piracy match.

    The Action Severity Score formula:
    ```
    ASS = (MatchConfidence × 0.4) + (ViewVelocityNorm × 0.25)
        + (ReputationInverse × 0.2) + (TransformationIndex × 0.15)
    ```

    Returns:
    - `action_id`: unique enforcement action identifier
    - `category`: TAKEDOWN | MONETIZE | LICENSE | MONITOR
    - `severity_score`: numeric score in [0, 1]
    - `ai_analysis`: Gemini AI recommendation + reasoning
    - `blockchain_hash`: SHA-256 hash chaining to the previous enforcement record
    """
    result = await enforcement_service.trigger_enforcement(
        action_data=data.model_dump(),
        user_id=current["user_id"],
    )
    logger.info(
        f"Enforcement triggered by {current['email']}: "
        f"{result['category']} (score={result['severity_score']:.3f})"
    )
    return result


@router.post(
    "/raw-alert",
    summary="Store a raw alert (no ARES processing)",
    description=(
        "Store a pre-built alert document directly in MongoDB alerts collection. "
        "Useful for alerts coming from the Telegram monitor or external integrations."
    ),
)
async def store_raw_alert(alert: AlertPayload):
    """
    **Store** a raw alert without running the full ARES pipeline.
    Accessible without authentication (used by the internal Telegram monitor).
    """
    db = get_db()
    doc = alert.model_dump()
    doc["created_at"] = datetime.now(timezone.utc).isoformat()

    if db is not None:
        result = await db.alerts.insert_one(doc)
        alert_id = str(result.inserted_id)
    else:
        alert_id = uuid.uuid4().hex

    logger.info(f"Raw alert stored: {alert_id}")
    return {"status": "ok", "alert_id": alert_id}


@router.get(
    "/logs",
    summary="Retrieve enforcement history",
    description=(
        "Return all ARES enforcement actions logged to MongoDB, "
        "sorted from most to least recent."
    ),
)
async def enforcement_logs(
    limit: int = Query(50, le=200, description="Max records to return"),
    skip: int = Query(0, description="Pagination offset"),
    current=Depends(get_current_user),
):
    """**Retrieve** the blockchain-backed enforcement action log."""
    logs = await enforcement_service.get_enforcement_logs(limit=limit, skip=skip)
    return {"logs": logs, "count": len(logs)}
