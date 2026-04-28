"""
services/deepfake_service.py — Deepfake video analysis service.

Wraps the CNN-LSTM model logic from the existing api.py and ml/model.py.
The model is loaded lazily on first request and cached globally.
"""

import os
import numpy as np
from typing import Optional

from config import settings
from utils.logging_utils import get_logger

logger = get_logger("piraksha.deepfake_service")

# ── Lazy-loaded model globals ─────────────────────────────────────────────────
_model = None
_tf_available = False
_cv2_available = False

MODEL_PATH = str(settings.BACKEND_DIR / "cnn_lstm_new_model.keras")
NUM_FRAMES = 20
FRAME_SIZE = (112, 112)


def _try_load_dependencies():
    global _tf_available, _cv2_available
    try:
        import cv2  # noqa: F401
        _cv2_available = True
    except ImportError:
        logger.warning("OpenCV not available — deepfake service limited")

    try:
        import tensorflow as tf  # noqa: F401
        _tf_available = True
    except ImportError:
        logger.warning("TensorFlow not available — deepfake service disabled")


def load_model() -> bool:
    """
    Attempt to load the deepfake model.
    Returns True if the model was successfully loaded.
    """
    global _model
    _try_load_dependencies()

    if not _tf_available:
        logger.info("Skipping model load (TensorFlow unavailable)")
        return False

    try:
        import tensorflow as tf
        from keras.layers import Dense

        # Patch incompatible quantization_config kwarg
        _orig_init = Dense.__init__

        def _patched_init(self, *args, **kwargs):
            kwargs.pop("quantization_config", None)
            _orig_init(self, *args, **kwargs)

        Dense.__init__ = _patched_init

        _model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        logger.info(f"Deepfake model loaded from {MODEL_PATH}")
        return True
    except Exception as exc:
        logger.warning(f"Deepfake model not loaded: {exc}")
        return False


def _extract_frames(video_path: str, num_frames: int = NUM_FRAMES) -> Optional[np.ndarray]:
    """Extract *num_frames* evenly-spaced frames from *video_path*."""
    import cv2

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total // num_frames, 1)
    frames = []
    for i in range(num_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, FRAME_SIZE).astype("float32") / 255.0
        frames.append(frame)
    cap.release()

    # Pad if needed
    while len(frames) < num_frames:
        if frames:
            frames.append(frames[-1])
        else:
            frames.append(np.zeros((*FRAME_SIZE, 3), dtype="float32"))

    return np.array(frames)


async def analyze_video(file_path: str) -> dict:
    """
    Run deepfake detection on *file_path*.

    Returns:
        {
          "prediction": 0 or 1,
          "probability": float,
          "label": "REAL" | "DEEPFAKE",
          "model_available": bool
        }
    """
    global _model

    if _model is None:
        loaded = load_model()
        if not loaded:
            return {
                "prediction": -1,
                "probability": 0.0,
                "label": "MODEL_UNAVAILABLE",
                "model_available": False,
            }

    if not _cv2_available:
        return {
            "prediction": -1,
            "probability": 0.0,
            "label": "OPENCV_UNAVAILABLE",
            "model_available": False,
        }

    try:
        frames = _extract_frames(file_path)
        frames_batch = np.expand_dims(frames, axis=0)
        preds = _model.predict(frames_batch, verbose=0)
        prob = float(preds[0][0])
        pred = int(prob > 0.5)
        label = "DEEPFAKE" if pred == 1 else "REAL"
        logger.info(f"Deepfake analysis: {label} ({prob:.4f})")
        return {
            "prediction": pred,
            "probability": prob,
            "label": label,
            "model_available": True,
        }
    except Exception as exc:
        logger.error(f"Deepfake analysis failed: {exc}", exc_info=True)
        raise
