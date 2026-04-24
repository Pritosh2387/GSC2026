import numpy as np
import tensorflow as tf
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import cv2
import tempfile
import os
import json

from keras.layers import Dense

original_init = Dense.__init__

def new_init(self, *args, **kwargs):
    kwargs.pop("quantization_config", None)
    original_init(self, *args, **kwargs)

Dense.__init__ = new_init

app = FastAPI(title="SportGuard AI — API")

MODEL_PATH = "cnn_lstm_new_model.keras"

# Graceful model loading — API still starts even without the .keras file
model = None
try:
    print("Loading deepfake model...")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("Model loaded successfully!")
except Exception as _model_err:
    print(f"⚠️  Deepfake model not loaded ({_model_err}). /predict-video will be unavailable.")

def extract_frames(video_path, num_frames=20):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception("Error opening video file")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total_frames // num_frames, 1)

    frames = []

    for i in range(num_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        ret, frame = cap.read()

        if not ret:
            break

        # Resize to match model input
        frame = cv2.resize(frame, (112, 112))

        # Normalize
        frame = frame.astype("float32") / 255.0

        frames.append(frame)

    cap.release()

    # Padding if frames < required
    while len(frames) < num_frames:
        frames.append(frames[-1])

    return np.array(frames)


@app.get("/")
def home():
    return {"message": "SportGuard AI API is running", "deepfake_model_loaded": model is not None}

@app.post("/predict-video")
async def predict_video(file: UploadFile = File(...)):
    temp_path = None

    if model is None:
        return {"error": "Deepfake model is not loaded. Upload the .keras file and restart."}

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await file.read())
            temp_path = tmp.name

        # Extract frames
        frames = extract_frames(temp_path)

        # Add batch dimension
        frames = np.expand_dims(frames, axis=0)

        # Prediction
        preds = model.predict(frames)
        prob = float(preds[0][0])
        label = int(prob > 0.5)

        return {
            "prediction": label,
            "probability": prob
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# ==========================================================================
# Telegram Integration Endpoints
# ==========================================================================
ALERTS_FILE = "telegram_alerts.json"
MATCHES_FILE = "telegram_matches.json"
REFERENCE_FILE = "reference_fingerprints.json"


class AlertPayload(BaseModel):
    type: str = "piracy_match"
    channel_name: Optional[str] = None
    message_id: Optional[int] = None
    similarity_score: Optional[float] = None
    matched_content: Optional[str] = None
    media_path: Optional[str] = None
    timestamp: Optional[str] = None
    severity: Optional[str] = None


def _read_json(path: str) -> list:
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


@app.post("/telegram-alerts")
async def receive_alert(alert: AlertPayload):
    """Receive a piracy-match alert from the Telegram monitor."""
    alerts = _read_json(ALERTS_FILE)
    alerts.append(alert.model_dump())
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)
    return {"status": "ok", "total_alerts": len(alerts)}


@app.get("/telegram-alerts")
def get_alerts():
    """Return all stored piracy-match alerts."""
    return _read_json(ALERTS_FILE)


@app.get("/telegram-matches")
def get_matches():
    """Return all Telegram match records."""
    return _read_json(MATCHES_FILE)


@app.post("/register-content")
async def register_content(file: UploadFile = File(...), content_name: str = "untitled"):
    """
    Register original content by uploading an image or video.
    Its fingerprint is computed and stored in the reference database.
    """
    from telegram.telegram_utils import (
        fingerprint_image, fingerprint_video, get_media_type, ReferenceDatabase,
    )

    suffix = os.path.splitext(file.filename or ".bin")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    try:
        media_type = get_media_type(temp_path)
        if media_type is None:
            return {"error": f"Unsupported file type: {suffix}"}

        if media_type == "image":
            fp = fingerprint_image(temp_path)
        else:
            fp = fingerprint_video(temp_path)

        if fp is None:
            return {"error": "Fingerprinting failed."}

        db = ReferenceDatabase()
        db.register(temp_path, content_name, media_type, fp)
        return {
            "status": "registered",
            "content_name": content_name,
            "media_type": media_type,
            "dimension": len(fp),
            "total_registered": len(db.entries),
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)