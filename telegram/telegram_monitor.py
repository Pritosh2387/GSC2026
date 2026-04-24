"""
telegram_monitor.py — SportGuard Telegram channel surveillance.

Monitors all joined Telegram channels/groups for media messages.
For every downloaded image or video:
  1. Checks for duplicates (SHA-256 file hash)
  2. Generates a fingerprint (DCT pHash for images, full 512-dim for videos)
  3. Compares against the reference fingerprint database
  4. If similarity ≥ threshold → stores the match and dispatches an alert
"""

import os
import sys
import logging
from datetime import datetime

# ---------------------------------------------------------------------------
# Path setup — ensure the project root is importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from telethon import TelegramClient
from telethon.events import NewMessage

from telegram.telegram_utils import (
    compute_file_hash,
    get_media_type,
    fingerprint_image,
    fingerprint_video,
    ReferenceDatabase,
    MatchResultStore,
    send_alert,
    SIMILARITY_THRESHOLD,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-24s | %(levelname)-7s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(PROJECT_ROOT, "telegram_monitor.log"),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("sportguard.telegram")

# ---------------------------------------------------------------------------
# Telegram credentials  (keep in sync with the original telegram_monitor.py)
# ---------------------------------------------------------------------------
api_id = 39575664
api_hash = "52cb3a87e3142e8d64800b89b573b9cd"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DOWNLOAD_FOLDER = os.path.join(PROJECT_ROOT, "media_downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ---------------------------------------------------------------------------
# Initialise shared components (loaded once at startup)
# ---------------------------------------------------------------------------
client = TelegramClient(
    os.path.join(PROJECT_ROOT, "session"),   # reuse existing session file
    api_id,
    api_hash,
)
ref_db = ReferenceDatabase()
match_store = MatchResultStore()


# ---------------------------------------------------------------------------
# Event handler — fires on every new message across all chats
# ---------------------------------------------------------------------------
@client.on(NewMessage) # type: ignore
async def handler(event):
    try:
        # ── 1. Skip non-media messages ──────────────────────────────────
        if not event.message.media:
            return

        logger.info("📩 New media detected!")

        # ── 2. Download the media ───────────────────────────────────────
        file_path = await event.message.download_media(file=DOWNLOAD_FOLDER)
        if not file_path:
            logger.warning("Download returned None — skipping.")
            return
        logger.info(f"✅ Downloaded: {file_path}")

        # ── 3. Gather channel / message metadata ───────────────────────
        chat = await event.get_chat()
        channel_name = getattr(chat, "title", "DM / Unknown")
        message_id = event.message.id
        timestamp = (
            event.message.date.isoformat()
            if event.message.date
            else datetime.now().isoformat()
        )
        logger.info(f"📢 Channel: {channel_name} | 🆔 Message ID: {message_id}")

        # ── 4. Duplicate detection (SHA-256) ────────────────────────────
        file_hash = compute_file_hash(file_path)
        if match_store.is_duplicate(file_hash):
            logger.info(
                f"⏭️  Duplicate media (hash {file_hash[:16]}…) — skipping."
            )
            return

        # ── 5. Media-type gate ──────────────────────────────────────────
        media_type = get_media_type(file_path)
        if media_type is None:
            logger.info(f"⏭️  Unsupported media type for {file_path} — skipping.")
            return

        # ── 6. Fingerprint ──────────────────────────────────────────────
        logger.info(f"🔍 Fingerprinting {media_type}: {os.path.basename(file_path)}")

        if media_type == "image":
            fingerprint = fingerprint_image(file_path)
        else:  # video
            fingerprint = fingerprint_video(file_path)

        if fingerprint is None:
            logger.warning(f"⚠️  Fingerprinting returned None for {file_path}")
            return

        # ── 7. Compare against reference database ──────────────────────
        matches = ref_db.find_matches(
            fingerprint, media_type, threshold=SIMILARITY_THRESHOLD
        )

        if not matches:
            logger.info(
                f"✅ No match above threshold ({SIMILARITY_THRESHOLD}) "
                f"for {os.path.basename(file_path)}"
            )
            return

        # ── 8. Store result + send alert for every match ────────────────
        best = matches[0]
        logger.info(
            f"🚨 MATCH FOUND! Score: {best['similarity_score']:.4f} "
            f"| Content: {best['content_name']}"
        )

        match_data = match_store.store_match(
            channel_name=channel_name,
            message_id=message_id,
            timestamp=timestamp,
            similarity_score=best["similarity_score"],
            media_path=file_path,
            media_type=media_type,
            matched_content=best["content_name"],
            file_hash=file_hash,
        )

        send_alert(match_data)
        logger.info(f"📊 Total reference matches for this file: {len(matches)}")

    except Exception as e:
        logger.error(f"❌ Error processing message: {e}", exc_info=True)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
def main():
    logger.info("🚀 SportGuard Telegram Monitor starting...")
    logger.info(f"📁 Download folder : {DOWNLOAD_FOLDER}")
    logger.info(f"📊 Reference DB    : {len(ref_db.entries)} entries")
    logger.info(f"🎯 Threshold       : {SIMILARITY_THRESHOLD}")

    client.start()
    client.run_until_disconnected()


if __name__ == "__main__":
    main()
