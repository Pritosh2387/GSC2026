"""
routes/deepfake.py — Deepfake analysis endpoint.

POST /api/deepfake/analyze — Run deepfake detection on a video file
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from auth import get_current_user
from services import deepfake_service
from utils.file_utils import save_upload_to_temp, cleanup_temp
from utils.logging_utils import get_logger

router = APIRouter(prefix="/api/deepfake", tags=["Deepfake Detection"])
logger = get_logger("piraksha.routes.deepfake")


@router.post(
    "/analyze",
    summary="Run deepfake detection on a video",
    description=(
        "Upload a video file. PIRAKSHA uses a CNN-LSTM model to classify "
        "each video as REAL or DEEPFAKE with a confidence probability.\n\n"
        "**Model**: `cnn_lstm_new_model.keras` (stored in backend/).\n"
        "If the model or TensorFlow is unavailable, the response will indicate "
        "MODEL_UNAVAILABLE but will not error."
    ),
)
async def analyze_deepfake(
    file: UploadFile = File(..., description="Video file (.mp4, .avi, .mkv, …)"),
    current=Depends(get_current_user),
):
    """
    **Analyze** a video for deepfake manipulation.

    Returns:
    - `prediction`: `0` = real, `1` = deepfake, `-1` = model unavailable
    - `probability`: confidence score in [0.0, 1.0]
    - `label`: `"REAL"` | `"DEEPFAKE"` | `"MODEL_UNAVAILABLE"`
    - `model_available`: whether the CNN-LSTM model was loaded
    """
    # Allow videos only
    filename = file.filename or ""
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    supported_video = {"mp4", "avi", "mkv", "mov", "webm", "flv", "wmv", "3gp"}
    if suffix not in supported_video:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported video format: .{suffix}. Accepted: {supported_video}",
        )

    temp_path = await save_upload_to_temp(file, suffix=f".{suffix}")
    try:
        result = await deepfake_service.analyze_video(temp_path)
        logger.info(
            f"Deepfake analysis: {result['label']} "
            f"(prob={result['probability']:.3f}) for {filename}"
        )
        return result
    except Exception as exc:
        logger.error(f"Deepfake analysis error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        cleanup_temp(temp_path)
