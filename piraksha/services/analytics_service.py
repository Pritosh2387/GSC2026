"""
services/analytics_service.py — Dashboard metrics and report generation.

Aggregates data from all MongoDB collections and returns structured
analytics suitable for the frontend dashboard.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

from database import get_db
from utils.logging_utils import get_logger

logger = get_logger("piraksha.analytics_service")


async def get_dashboard_metrics() -> dict:
    """
    Aggregate key metrics across all PIRAKSHA collections.

    Returns a unified dashboard stats object.
    """
    db = get_db()

    if db is None:
        return _empty_metrics()

    # Run all counts concurrently via asyncio.gather for speed
    import asyncio

    (
        total_alerts,
        unresolved_alerts,
        total_detections,
        total_media,
        total_fingerprints,
        total_users,
        total_evidence,
        high_severity,
        takedowns,
    ) = await asyncio.gather(
        db.alerts.count_documents({}),
        db.alerts.count_documents({"resolved": False}),
        db.detections.count_documents({}),
        db.media.count_documents({}),
        db.fingerprints.count_documents({}),
        db.users.count_documents({}),
        db.evidence.count_documents({}),
        db.alerts.count_documents({"severity": "high"}),
        db.evidence.count_documents({"category": "takedown"}),
    )

    # Recent activity — last 7 days
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_alerts = await db.alerts.count_documents({"created_at": {"$gte": seven_days_ago}})
    recent_detections = await db.detections.count_documents({"detected_at": {"$gte": seven_days_ago}})

    # Severity breakdown
    severity_breakdown = {}
    for sev in ("low", "medium", "high", "critical"):
        severity_breakdown[sev] = await db.alerts.count_documents({"severity": sev})

    # Top channels by violation count
    top_channels = []
    pipeline = [
        {"$group": {"_id": "$channel_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
    ]
    async for doc in db.alerts.aggregate(pipeline):
        if doc.get("_id"):
            top_channels.append({"channel": doc["_id"], "violations": doc["count"]})

    from services.telegram_service import MONITOR_RUNNING

    metrics = {
        "overview": {
            "total_alerts": total_alerts,
            "unresolved_alerts": unresolved_alerts,
            "total_detections": total_detections,
            "registered_media": total_media,
            "registered_fingerprints": total_fingerprints,
            "total_users": total_users,
            "enforcement_actions": total_evidence,
        },
        "severity": severity_breakdown,
        "recent_7_days": {
            "alerts": recent_alerts,
            "detections": recent_detections,
        },
        "enforcement": {
            "takedowns": takedowns,
            "high_severity_alerts": high_severity,
        },
        "top_channels": top_channels,
        "telegram_running": MONITOR_RUNNING,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Persist snapshot to analytics collection
    await db.analytics.insert_one({**metrics, "snapshot_type": "dashboard"})
    logger.info("Dashboard metrics generated and stored")
    return metrics


async def get_reports(limit: int = 20) -> list:
    """Retrieve previously generated analytics snapshots."""
    db = get_db()
    if db is None:
        return []
    cursor = db.analytics.find().sort("generated_at", -1).limit(limit)
    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        docs.append(doc)
    return docs


def _empty_metrics() -> dict:
    return {
        "overview": {
            "total_alerts": 0,
            "unresolved_alerts": 0,
            "total_detections": 0,
            "registered_media": 0,
            "registered_fingerprints": 0,
            "total_users": 0,
            "enforcement_actions": 0,
        },
        "severity": {"low": 0, "medium": 0, "high": 0, "critical": 0},
        "recent_7_days": {"alerts": 0, "detections": 0},
        "enforcement": {"takedowns": 0, "high_severity_alerts": 0},
        "top_channels": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "Database unavailable — returning empty metrics",
    }
