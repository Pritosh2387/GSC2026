"""
routes/alerts.py — Piracy alerts management.

GET    /api/alerts              — List all piracy alerts
PATCH  /api/alerts/{id}/resolve — Mark an alert as resolved
"""

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth import get_current_user
from database import get_db
from utils.logging_utils import get_logger

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])
logger = get_logger("piraksha.routes.alerts")


@router.get(
    "/",
    summary="List piracy alerts",
    description="Retrieve all piracy alerts detected by the system (e.g. from Telegram).",
)
async def list_alerts(
    severity: str = Query(None, description="Filter by severity"),
    resolved: bool = Query(None, description="Filter by resolution status"),
    limit: int = Query(50, le=200),
    skip: int = Query(0),
    current=Depends(get_current_user),
):
    db = get_db()
    if db is None:
        return []

    query = {}
    if severity and severity != "all":
        query["severity"] = severity
    if resolved is not None:
        query["resolved"] = resolved

    cursor = db.alerts.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        docs.append(doc)
    return docs


@router.patch(
    "/{alert_id}/resolve",
    summary="Resolve an alert",
    description="Mark a piracy alert as resolved/verified.",
)
async def resolve_alert(
    alert_id: str,
    current=Depends(get_current_user),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    try:
        result = await db.alerts.update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": {"resolved": True, "resolved_at": ""}} # Simplified
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        logger.info(f"Alert {alert_id} resolved by {current['email']}")
        return {"status": "resolved"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid alert ID")
