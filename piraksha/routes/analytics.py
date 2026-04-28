"""
routes/analytics.py — Analytics and reporting endpoints.

GET /api/analytics/dashboard — Return aggregated dashboard metrics
GET /api/analytics/reports   — Return previously generated analytics snapshots
"""

from fastapi import APIRouter, Depends, Query

from auth import get_current_user
from services import analytics_service
from utils.logging_utils import get_logger

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])
logger = get_logger("piraksha.routes.analytics")


@router.get(
    "/dashboard",
    summary="Dashboard metrics",
    description=(
        "Return a comprehensive set of real-time metrics aggregated from all "
        "PIRAKSHA collections:\n"
        "- Overview counts (alerts, detections, registered media, users)\n"
        "- Severity breakdown\n"
        "- Recent 7-day activity\n"
        "- Top violating channels\n"
        "- Enforcement summary\n\n"
        "Each call also persists a snapshot to the `analytics` collection."
    ),
)
async def dashboard(current=Depends(get_current_user)):
    """
    **Return** the PIRAKSHA dashboard metrics.

    All counts are live-queried from MongoDB.  The result is also stored
    as an analytics snapshot for historical reporting.
    """
    metrics = await analytics_service.get_dashboard_metrics()
    logger.info(f"Dashboard metrics fetched by {current['email']}")
    return metrics


@router.get(
    "/reports",
    summary="Return analytics report history",
    description=(
        "Return previously generated analytics snapshots stored in the "
        "`analytics` MongoDB collection, sorted most-recent first."
    ),
)
async def reports(
    limit: int = Query(20, le=100, description="Number of reports to return"),
    current=Depends(get_current_user),
):
    """**Retrieve** historical analytics snapshots."""
    data = await analytics_service.get_reports(limit=limit)
    logger.info(f"Analytics reports fetched by {current['email']}: {len(data)} record(s)")
    return {"reports": data, "count": len(data)}
