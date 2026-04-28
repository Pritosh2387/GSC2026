"""
services/watermark_service.py — Watermark embedding wrapper.

Wraps the existing SportGuard WatermarkEmbedder.  Because the embedder works
on raw numpy frame/audio arrays (not file paths), this service provides a
file-level convenience function and a metadata-only fallback for cases where
full video processing is not required in the API demo context.
"""

from typing import Optional
from utils.logging_utils import get_logger

logger = get_logger("piraksha.watermark_service")


def apply_watermark_to_media(
    file_path: str,
    user_info: dict,
) -> dict:
    """
    Attempt to apply multi-domain watermark to a media file.

    For video: extracts frames + audio → applies WatermarkEmbedder → returns metadata.
    For image: applies a simpler luminance-level mark.

    Returns a result dict with 'success' bool and 'message'.
    """
    try:
        import cv2
        import numpy as np
        from sportguard.watermarking.embedder import WatermarkEmbedder

        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            # Try treating as image
            frame = cv2.imread(file_path)
            if frame is None:
                return {"success": False, "message": "Cannot open media file"}

            from sportguard.watermarking.luminance import LuminanceWatermark
            from sportguard.watermarking.encoder import WatermarkPayload

            payload = WatermarkPayload(
                user_id=user_info.get("user_id", "u0"),
                device_id=user_info.get("device_id", "d0"),
                tier=user_info.get("tier", "standard"),
                region=user_info.get("region", "IN"),
            )
            bits = np.unpackbits(np.frombuffer(payload.encode_128bit(), dtype=np.uint8))
            lum = LuminanceWatermark()
            lum.embed(frame, bits)
            logger.info(f"Image watermark applied for user {user_info.get('user_id')}")
            return {"success": True, "message": "Luminance watermark embedded (image)"}

        # Video path
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()

        if not frames:
            return {"success": False, "message": "No frames extracted from video"}

        # Generate dummy audio samples (real pipeline would decode audio track)
        sr = 44100
        dummy_audio = np.zeros(sr, dtype=np.float32)

        embedder = WatermarkEmbedder()
        w_frames, w_audio, jitters = embedder.apply_watermark(
            frames, dummy_audio, user_info, sr
        )
        logger.info(
            f"Video watermark applied — {len(w_frames)} frames, "
            f"user={user_info.get('user_id')}"
        )
        return {
            "success": True,
            "message": f"Watermark embedded in {len(w_frames)} frame(s)",
        }

    except Exception as exc:
        logger.error(f"Watermarking failed: {exc}", exc_info=True)
        return {"success": False, "message": f"Watermark error: {exc}"}
