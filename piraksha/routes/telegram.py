"""
routes/telegram.py — Telegram monitoring control endpoints.

POST /api/telegram/start-monitor   — Start background Telegram surveillance
POST /api/telegram/stop-monitor    — Stop the monitor
GET  /api/telegram/channels        — List channels seen in match history
GET  /api/telegram/media           — List downloaded Telegram media files
GET  /api/telegram/status          — Monitor status (running / session exists)
"""

from fastapi import APIRouter, Depends

from auth import get_current_user
from services import telegram_service
from utils.logging_utils import get_logger

router = APIRouter(prefix="/api/telegram", tags=["Telegram Monitor"])
logger = get_logger("piraksha.routes.telegram")


@router.post(
    "/start-monitor",
    summary="Start Telegram monitoring",
    description=(
        "Launch the background Telegram channel surveillance. "
        "Requires TELEGRAM_API_ID and TELEGRAM_API_HASH to be set in .env "
        "and a valid Telethon session file to exist."
    ),
)
async def start_monitor(current=Depends(get_current_user)):
    """
    **Start** the Telegram media monitor.

    The monitor listens on all joined channels / groups for new media messages.
    Each download is fingerprinted and compared against the reference database.
    Matches above the similarity threshold are stored as alerts in MongoDB.
    """
    result = await telegram_service.start_monitor()
    logger.info(f"Telegram monitor start requested by {current['email']}")
    return result


@router.post(
    "/stop-monitor",
    summary="Stop Telegram monitoring",
    description="Gracefully disconnect the Telegram client and stop monitoring.",
)
async def stop_monitor(current=Depends(get_current_user)):
    """**Stop** the active Telegram monitor session."""
    result = await telegram_service.stop_monitor()
    logger.info(f"Telegram monitor stopped by {current['email']}")
    return result


@router.get(
    "/channels",
    summary="List monitored channels",
    description=(
        "Return a list of unique channel names that have appeared in the "
        "piracy match history (loaded from the local JSON match store)."
    ),
)
async def list_channels(current=Depends(get_current_user)):
    """
    **List** all Telegram channels where piracy matches have been detected.

    Data is sourced from the local `telegram_matches.json` store.
    """
    channels = telegram_service.list_channels()
    return {"channels": channels, "count": len(channels)}


@router.get(
    "/media",
    summary="List downloaded Telegram media",
    description=(
        "Return metadata for all media files downloaded by the Telegram monitor "
        "(stored in backend/media_downloads/)."
    ),
)
async def list_media(current=Depends(get_current_user)):
    """**List** all media files captured by the Telegram monitor."""
    media = telegram_service.list_downloaded_media()
    return {"media": media, "count": len(media)}


@router.get(
    "/status",
    summary="Telegram monitor status",
    description="Check whether the Telegram monitor is currently running.",
)
async def monitor_status(current=Depends(get_current_user)):
    """Return current monitor status including session availability."""
    return await telegram_service.get_status()
