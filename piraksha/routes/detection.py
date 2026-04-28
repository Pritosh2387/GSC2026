"""
routes/detection.py — Media piracy detection endpoints.

POST /api/detection/run     — Run detection on uploaded media
GET  /api/detection/results — Retrieve stored detection history
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends, Query

from auth import get_current_user
from services import detection_service
from utils.file_utils import save_upload_to_temp, cleanup_temp
from utils.logging_utils import get_logger

router = APIRouter(prefix="/api/detection", tags=["Detection"])
logger = get_logger("piraksha.routes.detection")


@router.post(
    "/run",
    summary="Run piracy detection on uploaded media",
    description=(
        "Upload a media file. PIRAKSHA fingerprints it and compares against all "
        "registered reference content. Returns matches sorted by similarity score."
    ),
)
async def run_detection(
    file: UploadFile = File(..., description="Image or video to check"),
    threshold: float = Form(0.9, description="Similarity threshold (0.0–1.0)"),
    current=Depends(get_current_user),
):
    """
    **Run** end-to-end piracy detection on the uploaded file.

    Steps:
    1. Fingerprint the uploaded file
    2. Compare against all registered reference fingerprints
    3. Return any matches above the threshold
    4. Persist detection result to MongoDB `detections` collection
    """
    temp_path = await save_upload_to_temp(file)
    try:
        result = await detection_service.run_detection(
            file_path=temp_path,
            threshold=threshold,
            user_id=current["user_id"],
        )
        logger.info(
            f"Detection run on {file.filename}: "
            f"{result.get('matches_found', 0)} match(es)"
        )
        return result
    finally:
        cleanup_temp(temp_path)


@router.get(
    "/results",
    summary="Get detection history",
    description=(
        "Return all previously run detection results stored in MongoDB, "
        "sorted from most to least recent."
    ),
)
async def detection_results(
    limit: int = Query(50, le=200, description="Max results to return"),
    skip: int = Query(0, description="Pagination offset"),
    current=Depends(get_current_user),
):
    """**Retrieve** detection history from the `detections` collection."""
    results = await detection_service.get_detection_results(limit=limit, skip=skip)
    return {"results": results, "count": len(results)}
