"""
routes/fingerprint.py — Fingerprint generation and comparison endpoints.

POST /api/fingerprint/generate  — Generate fingerprint for uploaded media
POST /api/fingerprint/compare   — Compare uploaded media against stored fingerprints
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import JSONResponse

from auth import get_current_user
from services import fingerprint_service
from utils.file_utils import save_upload_to_temp, cleanup_temp
from utils.logging_utils import get_logger

router = APIRouter(prefix="/api/fingerprint", tags=["Fingerprint"])
logger = get_logger("piraksha.routes.fingerprint")


@router.post(
    "/generate",
    summary="Generate fingerprint for media",
    description=(
        "Upload an image or video file. "
        "Returns the fingerprint dimensionality and media type. "
        "Does NOT store in reference DB — use /api/media/register for that."
    ),
)
async def generate_fingerprint(
    file: UploadFile = File(..., description="Image or video file"),
    current=Depends(get_current_user),
):
    """
    **Generate** a perceptual fingerprint for the uploaded media file.

    - Images: 128-dim DCT perceptual hash
    - Videos: 512-dim fused fingerprint (visual + audio + temporal + semantic)

    Does NOT persist to the database. Use `/api/media/register` to register content.
    """
    temp_path = await save_upload_to_temp(file)
    try:
        fp, media_type = fingerprint_service.generate_fingerprint(temp_path)
        if fp is None:
            raise HTTPException(
                status_code=422,
                detail=f"Fingerprinting failed — unsupported or corrupt file: {file.filename}",
            )
        logger.info(f"Fingerprint generated: {media_type}, {len(fp)}-dim for {file.filename}")
        return {
            "status": "ok",
            "filename": file.filename,
            "media_type": media_type,
            "fingerprint_dim": len(fp),
            # Only return a snippet of the vector to keep the response lean
            "fingerprint_preview": fp[:8].tolist(),
        }
    finally:
        cleanup_temp(temp_path)


@router.post(
    "/compare",
    summary="Compare media against reference fingerprints",
    description=(
        "Upload media and compare its fingerprint against all registered "
        "reference fingerprints. Returns similarity scores for each match."
    ),
)
async def compare_fingerprint(
    file: UploadFile = File(..., description="Media file to compare"),
    threshold: float = Form(0.9, description="Minimum similarity threshold (0–1)"),
    current=Depends(get_current_user),
):
    """
    **Compare** uploaded media fingerprint against the reference database.

    Returns all registered content items whose similarity score exceeds
    the specified threshold, sorted from highest to lowest similarity.
    """
    temp_path = await save_upload_to_temp(file)
    try:
        fp, media_type = fingerprint_service.generate_fingerprint(temp_path)
        if fp is None:
            raise HTTPException(
                status_code=422,
                detail=f"Could not fingerprint {file.filename}",
            )

        matches = fingerprint_service.compare_against_db(fp, media_type, threshold=threshold)
        logger.info(f"Comparison: {len(matches)} match(es) for {file.filename}")
        return {
            "status": "ok",
            "filename": file.filename,
            "media_type": media_type,
            "fingerprint_dim": len(fp),
            "threshold": threshold,
            "matches_found": len(matches),
            "matches": matches,
        }
    finally:
        cleanup_temp(temp_path)
