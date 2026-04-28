"""
routes/watermark.py — Media registration and watermark embedding endpoints.

POST /api/media/register  — Upload original media, generate fingerprint and store
POST /api/media/watermark — Embed forensic watermark into uploaded media
"""

from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException

from auth import get_current_user
from database import get_db
from services import fingerprint_service, watermark_service
from utils.file_utils import save_upload_to_temp, cleanup_temp
from utils.logging_utils import get_logger

router = APIRouter(prefix="/api/media", tags=["Media & Watermark"])
logger = get_logger("piraksha.routes.watermark")


@router.post(
    "/register",
    summary="Register original media (generates fingerprint)",
    description=(
        "Upload original media content. "
        "PIRAKSHA will fingerprint it and store the registration in MongoDB and the "
        "local reference database. Future uploads will be compared against this entry."
    ),
)
async def register_media(
    file: UploadFile = File(..., description="Original image or video to protect"),
    content_name: str = Form("untitled", description="Human-readable name for this content"),
    current=Depends(get_current_user),
):
    """
    **Register** an original media asset with PIRAKSHA.

    1. Saves the upload temporarily
    2. Detects media type (image / video)
    3. Generates fingerprint (128-dim for images, 512-dim for videos)
    4. Stores fingerprint in MongoDB `fingerprints` + `media` collections
    5. Persists to local JSON reference database for real-time Telegram matching
    """
    temp_path = await save_upload_to_temp(file)
    try:
        fp, media_type = fingerprint_service.generate_fingerprint(temp_path)
        if fp is None:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported or corrupt file: {file.filename}",
            )

        now = datetime.now(timezone.utc).isoformat()

        # Persist to MongoDB
        db = get_db()
        media_id = None
        if db is not None:
            media_doc = {
                "content_name": content_name,
                "filename": file.filename,
                "media_type": media_type,
                "fingerprint_dim": len(fp),
                "registered_at": now,
                "registered_by": current["user_id"],
            }
            result = await db.media.insert_one(media_doc)
            media_id = str(result.inserted_id)

            fp_doc = {
                "content_name": content_name,
                "media_id": media_id,
                "media_type": media_type,
                "fingerprint_dim": len(fp),
                "fingerprint": fp.tolist(),
                "registered_at": now,
                "registered_by": current["user_id"],
            }
            await db.fingerprints.insert_one(fp_doc)

        # Register in local JSON reference DB for live Telegram matching
        fingerprint_service.register_in_reference_db(
            temp_path, content_name, media_type, fp
        )

        logger.info(f"Media registered: '{content_name}' ({media_type}, {len(fp)}-dim)")
        return {
            "status": "registered",
            "content_name": content_name,
            "media_type": media_type,
            "fingerprint_dim": len(fp),
            "media_id": media_id,
            "registered_at": now,
        }
    finally:
        cleanup_temp(temp_path)


@router.post(
    "/watermark",
    summary="Embed forensic watermark into media",
    description=(
        "Upload a media file along with user/device metadata. "
        "PIRAKSHA embeds an invisible multi-domain forensic watermark "
        "(luminance + audio + temporal jitter) that can later identify the source leaker."
    ),
)
async def watermark_media(
    file: UploadFile = File(..., description="Media file to watermark"),
    user_id: str = Form(..., description="Subscriber / user ID"),
    device_id: str = Form(..., description="Device fingerprint ID"),
    tier: str = Form("standard", description="Subscription tier"),
    region: str = Form("IN", description="Region / jurisdiction code"),
    content_name: str = Form("untitled", description="Content title"),
    current=Depends(get_current_user),
):
    """
    **Embed** a forensic watermark into the uploaded media file.

    The watermark encodes a 128-bit payload containing user_id, device_id,
    tier, and region — allowing piracy attribution even after re-encoding.
    """
    user_info = {
        "user_id": user_id,
        "device_id": device_id,
        "tier": tier,
        "region": region,
    }

    temp_path = await save_upload_to_temp(file)
    try:
        result = watermark_service.apply_watermark_to_media(temp_path, user_info)
        logger.info(
            f"Watermark {'applied' if result['success'] else 'failed'} "
            f"for {file.filename} → user={user_id}"
        )
        return {
            "status": "ok" if result["success"] else "error",
            "content_name": content_name,
            "watermark_applied": result["success"],
            "message": result["message"],
        }
    finally:
        cleanup_temp(temp_path)
