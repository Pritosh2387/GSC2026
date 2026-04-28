"""
services/telegram_service.py — Telegram monitoring state management.

Wraps the existing telethon-based monitor from backend/telegram/telegram_monitor.py
and exposes start / stop / status / channel / media helpers for the route layer.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional

from config import settings
from utils.logging_utils import get_logger

logger = get_logger("piraksha.telegram_service")

# ── Shared monitor state ──────────────────────────────────────────────────────
MONITOR_RUNNING: bool = False
_telegram_client = None  # telethon TelegramClient instance
_monitor_task: Optional[asyncio.Task] = None


async def _run_monitor_loop() -> None:
    """
    Internal coroutine that mirrors api.py's run_telegram_monitor() but is
    managed here so the route layer only calls start/stop helpers.
    """
    global _telegram_client, MONITOR_RUNNING

    from telethon import TelegramClient, events
    from telegram.telegram_utils import (
        compute_file_hash, get_media_type,
        fingerprint_image, fingerprint_video,
        ReferenceDatabase, MatchResultStore,
    )
    from database import get_db
    from datetime import datetime, timezone

    api_id_str = settings.TELEGRAM_API_ID
    api_hash = settings.TELEGRAM_API_HASH

    if not api_id_str or not api_hash:
        logger.error("Missing TELEGRAM_API_ID / TELEGRAM_API_HASH in .env")
        return

    _telegram_client = TelegramClient(
        settings.SESSION_PATH, int(api_id_str), api_hash
    )
    await _telegram_client.start()
    MONITOR_RUNNING = True
    logger.info("Telegram Monitor started")

    ref_db = ReferenceDatabase(db_path=str(settings.REFERENCE_FP_JSON))
    match_store = MatchResultStore(db_path=str(settings.MATCHES_JSON))
    download_dir = str(settings.BACKEND_DIR / "media_downloads")
    os.makedirs(download_dir, exist_ok=True)

    @_telegram_client.on(events.NewMessage)
    async def _handler(event):
        if not event.message.media:
            return
        try:
            file_path = await event.message.download_media(file=download_dir)
            if not file_path:
                return
            chat = await event.get_chat()
            channel_name = getattr(chat, "title", "Unknown")
            file_hash = compute_file_hash(file_path)
            if match_store.is_duplicate(file_hash):
                return
            media_type = get_media_type(file_path)
            if media_type is None:
                return
            fp = (
                fingerprint_image(file_path)
                if media_type == "image"
                else fingerprint_video(file_path)
            )
            if fp is None:
                return
            matches = ref_db.find_matches(fp, media_type, threshold=settings.SIMILARITY_THRESHOLD)
            if matches:
                best = matches[0]
                db = get_db()
                if db is not None:
                    alert_doc = {
                        "type": "piracy_match",
                        "channel_name": channel_name,
                        "message_id": event.message.id,
                        "similarity_score": best["similarity_score"],
                        "matched_content": best["content_name"],
                        "media_path": file_path,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "severity": "high" if best["similarity_score"] > 0.9 else "medium",
                        "resolved": False,
                    }
                    await db.alerts.insert_one(alert_doc)
                    await db.detections.insert_one({
                        **alert_doc,
                        "detected_at": datetime.now(timezone.utc).isoformat(),
                        "file_hash": file_hash,
                    })
                logger.info(
                    f"MATCH: {channel_name} | score={best['similarity_score']:.3f} "
                    f"| content={best['content_name']}"
                )
        except Exception as exc:
            logger.error(f"Monitor handler error: {exc}", exc_info=True)

    try:
        await _telegram_client.run_until_disconnected()
    finally:
        MONITOR_RUNNING = False
        logger.info("Telegram Monitor stopped")


async def start_monitor() -> dict:
    global _monitor_task, MONITOR_RUNNING
    if MONITOR_RUNNING:
        return {"status": "already_running"}
    _monitor_task = asyncio.create_task(_run_monitor_loop())
    return {"status": "starting"}


async def stop_monitor() -> dict:
    global _telegram_client, MONITOR_RUNNING
    if _telegram_client:
        await _telegram_client.disconnect()
    MONITOR_RUNNING = False
    return {"status": "stopped"}


async def get_status() -> dict:
    """Return comprehensive monitor status and live statistics."""
    from database import get_db
    
    session_exists = Path(settings.SESSION_PATH + ".session").exists()
    api_id = settings.TELEGRAM_API_ID
    masked_id = f"{api_id[:3]}***" if api_id and len(api_id) > 3 else "Not Set"
    
    # Aggregated Stats
    db = get_db()
    total_matches = 0
    unique_channels = 0
    avg_confidence = 0.0
    last_match = "Never"
    
    if db is not None:
        total_matches = await db.alerts.count_documents({"type": "piracy_match"})
        
        # Count unique channels via aggregation
        pipeline_chan = [{"$match": {"channel_name": {"$ne": None}}}, {"$group": {"_id": "$channel_name"}}, {"$count": "total"}]
        agg_chan = await db.alerts.aggregate(pipeline_chan).to_list(1)
        unique_channels = agg_chan[0]["total"] if agg_chan else 0

        # Avg Confidence & Last Match
        if total_matches > 0:
            pipeline_stats = [
                {"$match": {"type": "piracy_match"}},
                {"$group": {
                    "_id": None,
                    "avg_score": {"$avg": "$similarity_score"},
                    "latest": {"$max": "$created_at"}
                }}
            ]
            agg_stats = await db.alerts.aggregate(pipeline_stats).to_list(1)
            if agg_stats:
                avg_confidence = agg_stats[0]["avg_score"] or 0.0
                last_match = agg_stats[0]["latest"] or "Never"

    # Media count & Storage from local filesystem
    download_dir = settings.BACKEND_DIR / "media_downloads"
    media_count = 0
    storage_bytes = 0
    if download_dir.exists():
        for f in download_dir.iterdir():
            if f.is_file():
                media_count += 1
                storage_bytes += f.stat().st_size
    
    storage_mb = round(storage_bytes / (1024 * 1024), 2)

    return {
        "running": MONITOR_RUNNING,
        "api_id": masked_id,
        "api_id_set": bool(api_id),
        "session_exists": session_exists,
        "stats": {
            "total_matches": total_matches,
            "unique_channels": unique_channels,
            "media_captured": media_count,
            "forensic_storage_mb": storage_mb,
            "average_confidence": round(avg_confidence * 100, 1),
            "last_match_time": last_match
        }
    }


def list_downloaded_media() -> list:
    """Return a list of downloaded media files with basic metadata."""
    download_dir = settings.BACKEND_DIR / "media_downloads"
    if not download_dir.exists():
        return []
    files = []
    for f in download_dir.iterdir():
        if f.is_file():
            files.append({
                "filename": f.name,
                "size_bytes": f.stat().st_size,
                "path": str(f),
            })
    return files


def list_channels() -> list:
    """
    Return the list of channels referenced in stored matches/alerts.
    Reads the local JSON match store as the live Telethon session may not be active.
    """
    import json

    matches_path = settings.MATCHES_JSON
    if not matches_path.exists():
        return []
    try:
        with open(matches_path, "r") as fh:
            records = json.load(fh)
        channels = list({r.get("channel_name") for r in records if r.get("channel_name")})
        return channels
    except Exception:
        return []
