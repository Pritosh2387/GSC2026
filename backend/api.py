"""
api.py — SportGuard AI unified FastAPI server.

Provides:
  - JWT authentication (register / login / me)
  - Dashboard stats
  - Alert & match CRUD (MongoDB-backed)
  - Content registration (fingerprinting)
  - Deepfake video prediction
  - ARES decision-engine analysis
  - Telegram monitor control
"""

import os
import uuid
import json
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import numpy as np
from bson import ObjectId
from fastapi import (
    FastAPI, UploadFile, File, Form, Depends, HTTPException,
    status, Query,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import connect_to_mongo, close_mongo, get_db, is_connected
from auth import (
    UserCreate, UserLogin, TokenResponse, UserResponse,
    hash_password, verify_password, create_access_token, get_current_user,
)

# ---------------------------------------------------------------------------
# Heavy imports availability
# ---------------------------------------------------------------------------
TF_AVAILABLE = False
try:
    import cv2
    import tensorflow as tf
    from keras.layers import Dense

    original_init = Dense.__init__
    def _patched_init(self, *args, **kwargs):
        kwargs.pop("quantization_config", None)
        original_init(self, *args, **kwargs)
    Dense.__init__ = _patched_init
    CV2_AVAILABLE = True
    TF_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    TF_AVAILABLE = False

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="SportGuard AI — API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    await connect_to_mongo()
    # Try loading the deepfake model
    global deepfake_model
    MODEL_PATH = "cnn_lstm_new_model.keras"
    if TF_AVAILABLE:
        try:
            deepfake_model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            print("Deepfake model loaded")
        except Exception as e:
            deepfake_model = None
            print(f"Deepfake model not loaded: {e}")
    else:
        deepfake_model = None
        print("TensorFlow not installed; skipping deepfake model load.")

    # Create MongoDB Indices
    db = get_db()
    if db is not None:
        try:
            await db.users.create_index("email", unique=True)
            await db.alerts.create_index([("created_at", -1)])
            await db.alerts.create_index("severity")
            await db.matches.create_index([("detected_at", -1)])
            await db.ares_results.create_index([("analyzed_at", -1)])
            print("Database indices verified/created")
        except Exception as e:
            print(f"Index creation failed: {e}")


@app.on_event("shutdown")
async def shutdown():
    await close_mongo()
    global telegram_client
    if telegram_client:
        await telegram_client.disconnect()


deepfake_model = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _oid(doc: dict) -> dict:
    """Convert MongoDB ObjectId to string for JSON serialisation."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ===========================  AUTH  =========================================

@app.post("/auth/register", response_model=TokenResponse, status_code=201)
async def register(user: UserCreate):
    db = get_db()
    if db is None:
        raise HTTPException(503, "Database unavailable")

    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(400, "Email already registered")

    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "name": user.name,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "created_at": now,
    }
    result = await db.users.insert_one(doc)
    uid = str(result.inserted_id)

    token = create_access_token({"sub": uid, "email": user.email})
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=uid, name=user.name, email=user.email, created_at=now),
    )


@app.post("/auth/login", response_model=TokenResponse)
async def login(creds: UserLogin):
    db = get_db()
    if db is None:
        raise HTTPException(503, "Database unavailable")

    user = await db.users.find_one({"email": creds.email})
    if not user or not verify_password(creds.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")

    uid = str(user["_id"])
    token = create_access_token({"sub": uid, "email": user["email"]})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=uid,
            name=user["name"],
            email=user["email"],
            created_at=user.get("created_at", ""),
        ),
    )


@app.get("/auth/me", response_model=UserResponse)
async def me(current=Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(current["user_id"])})
    if not user:
        raise HTTPException(404, "User not found")
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user.get("created_at", ""),
    )


# ===========================  DASHBOARD  ====================================

@app.get("/")
async def root():
    return {"status": "ok", "service": "SportGuard AI", "deepfake_model": deepfake_model is not None}


@app.get("/dashboard/stats")
async def dashboard_stats(current=Depends(get_current_user)):
    db = get_db()
    if db is None:
        return {"alerts": 0, "matches": 0, "content": 0, "users": 0, "telegram_running": TELEGRAM_MONITOR_RUNNING}

    alerts = await db.alerts.count_documents({})
    matches = await db.matches.count_documents({})
    content = await db.reference_fingerprints.count_documents({})
    users = await db.users.count_documents({})
    unresolved = await db.alerts.count_documents({"resolved": False})

    return {
        "alerts": alerts,
        "matches": matches,
        "content": content,
        "users": users,
        "unresolved_alerts": unresolved,
        "telegram_running": TELEGRAM_MONITOR_RUNNING
    }


# ===========================  ALERTS  =======================================

class AlertPayload(BaseModel):
    type: str = "piracy_match"
    channel_name: Optional[str] = None
    message_id: Optional[int] = None
    similarity_score: Optional[float] = None
    matched_content: Optional[str] = None
    media_path: Optional[str] = None
    timestamp: Optional[str] = None
    severity: Optional[str] = "medium"
    resolved: bool = False


@app.post("/alerts")
async def create_alert(alert: AlertPayload):
    db = get_db()
    doc = alert.model_dump()
    doc["created_at"] = datetime.now(timezone.utc).isoformat()

    if db is not None:
        result = await db.alerts.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
    else:
        doc["_id"] = uuid.uuid4().hex

    return {"status": "ok", "alert_id": doc["_id"]}


@app.get("/alerts")
async def list_alerts(
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = Query(50, le=200),
    skip: int = 0,
    current=Depends(get_current_user),
):
    db = get_db()
    if db is None:
        return []

    query = {}
    if severity:
        query["severity"] = severity
    if resolved is not None:
        query["resolved"] = resolved

    cursor = db.alerts.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = []
    async for doc in cursor:
        docs.append(_oid(doc))
    return docs


@app.patch("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, current=Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(503, "Database unavailable")
    result = await db.alerts.update_one(
        {"_id": ObjectId(alert_id)}, {"$set": {"resolved": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(404, "Alert not found")
    return {"status": "resolved"}


# ===========================  MATCHES  ======================================

@app.get("/matches")
async def list_matches(
    limit: int = Query(50, le=200),
    skip: int = 0,
    current=Depends(get_current_user),
):
    db = get_db()
    if db is None:
        return []

    cursor = db.matches.find().sort("detected_at", -1).skip(skip).limit(limit)
    docs = []
    async for doc in cursor:
        docs.append(_oid(doc))
    return docs


# ===========================  CONTENT REGISTRATION  =========================

@app.post("/register-content")
async def register_content(
    file: UploadFile = File(...),
    content_name: str = Form("untitled"),
    current=Depends(get_current_user),
):
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

        fp = fingerprint_image(temp_path) if media_type == "image" else fingerprint_video(temp_path)
        if fp is None:
            return {"error": "Fingerprinting failed"}

        # Store in MongoDB
        db = get_db()
        doc = {
            "content_name": content_name,
            "media_type": media_type,
            "fingerprint_dim": len(fp),
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "registered_by": current["user_id"],
        }
        if db is not None:
            await db.reference_fingerprints.insert_one(doc)

        # Also register in the local JSON reference DB
        ref_db = ReferenceDatabase()
        ref_db.register(temp_path, content_name, media_type, fp)

        return {
            "status": "registered",
            "content_name": content_name,
            "media_type": media_type,
            "fingerprint_dim": len(fp),
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ===========================  DEEPFAKE  =====================================

def _extract_frames(video_path, num_frames=20):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("Cannot open video")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total // num_frames, 1)
    frames = []
    for i in range(num_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (112, 112)).astype("float32") / 255.0
        frames.append(frame)
    cap.release()
    while len(frames) < num_frames:
        frames.append(frames[-1])
    return np.array(frames)


@app.post("/predict-video")
async def predict_video(
    file: UploadFile = File(...),
    current=Depends(get_current_user),
):
    if deepfake_model is None:
        raise HTTPException(503, "Deepfake model not loaded")
    if not CV2_AVAILABLE:
        raise HTTPException(503, "OpenCV not available")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    try:
        frames = _extract_frames(temp_path)
        frames = np.expand_dims(frames, axis=0)
        preds = deepfake_model.predict(frames)
        prob = float(preds[0][0])
        return {"prediction": int(prob > 0.5), "probability": prob}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ===========================  ARES  =========================================

class AresMatchInput(BaseModel):
    match_id: str = "MANUAL_001"
    content_id: str = "UNKNOWN_CONTENT"
    match_confidence: float = 0.9
    transformation_index: float = 0.8
    view_velocity: float = 500.0
    platform: str = "youtube"
    uploader_id: str = "unknown"
    uploader_reputation: float = 1.0
    jurisdiction: str = "US"
    is_commercial: bool = False


@app.post("/ares/analyze")
async def ares_analyze(data: AresMatchInput, current=Depends(get_current_user)):
    from ares.models import MatchMetadata, Platform
    from ares.engine import DecisionEngine, MockGeminiAdapter

    platform_map = {
        "youtube": Platform.YOUTUBE,
        "meta": Platform.META,
        "tiktok": Platform.TIKTOK,
        "x": Platform.X,
    }

    match = MatchMetadata(
        match_id=data.match_id,
        content_id=data.content_id,
        match_confidence=data.match_confidence,
        transformation_index=data.transformation_index,
        view_velocity=data.view_velocity,
        platform=platform_map.get(data.platform.lower(), Platform.YOUTUBE),
        uploader_id=data.uploader_id,
        uploader_reputation=data.uploader_reputation,
        jurisdiction=data.jurisdiction,
        is_commercial=data.is_commercial,
    )

    engine = DecisionEngine(MockGeminiAdapter())
    category, score, ai_analysis = engine.classify(match)

    # Store in MongoDB
    db = get_db()
    result_doc = {
        "match_id": data.match_id,
        "content_id": data.content_id,
        "category": category.value,
        "severity_score": score,
        "ai_reasoning": ai_analysis.get("reasoning", ""),
        "ai_suggested_action": ai_analysis.get("suggested_action", ""),
        "parody_probability": ai_analysis.get("parody_probability", 0),
        "commercial_intent": ai_analysis.get("commercial_intent", ""),
        "platform": data.platform,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "analyzed_by": current["user_id"],
    }
    if db is not None:
        await db.ares_results.insert_one(result_doc)

    return {
        "category": category.value,
        "severity_score": score,
        "ai_analysis": ai_analysis,
    }


@app.get("/ares/history")
async def ares_history(
    limit: int = Query(20, le=100),
    current=Depends(get_current_user),
):
    db = get_db()
    if db is None:
        return []
    cursor = db.ares_results.find().sort("analyzed_at", -1).limit(limit)
    docs = []
    async for doc in cursor:
        docs.append(_oid(doc))
    return docs


# ---------------------------------------------------------------------------
# Telegram Monitor Integration
# ---------------------------------------------------------------------------
from telethon import TelegramClient, events
from telegram.telegram_utils import (
    compute_file_hash, get_media_type, fingerprint_image, fingerprint_video,
    ReferenceDatabase, MatchResultStore, send_alert, SIMILARITY_THRESHOLD
)

TELEGRAM_MONITOR_RUNNING = False
telegram_client: Optional[TelegramClient] = None
telegram_monitor_task: Optional[asyncio.Task] = None

async def run_telegram_monitor():
    global telegram_client, TELEGRAM_MONITOR_RUNNING
    
    api_id_str = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    if not api_id_str or not api_hash:
        print("Missing Telegram credentials")
        return
    api_id = int(api_id_str)
    
    session_path = str(Path(__file__).resolve().parent / "session")
    telegram_client = TelegramClient(session_path, api_id, api_hash)
    
    await telegram_client.start()
    TELEGRAM_MONITOR_RUNNING = True
    print("Telegram Monitor started")

    ref_db = ReferenceDatabase()
    match_store = MatchResultStore()
    download_folder = str(Path(__file__).resolve().parent / "media_downloads")
    os.makedirs(download_folder, exist_ok=True)

    @telegram_client.on(events.NewMessage)
    async def handler(event):
        if not event.message.media: return
        try:
            file_path = await event.message.download_media(file=download_folder)
            if not file_path: return
            chat = await event.get_chat()
            channel_name = getattr(chat, "title", "Unknown")
            file_hash = compute_file_hash(file_path)
            if match_store.is_duplicate(file_hash): return
            media_type = get_media_type(file_path)
            if media_type is None: return
            fp = fingerprint_image(file_path) if media_type == "image" else fingerprint_video(file_path)
            if fp is None: return
            matches = ref_db.find_matches(fp, media_type, threshold=SIMILARITY_THRESHOLD)
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
                        "resolved": False
                    }
                    await db.alerts.insert_one(alert_doc)
        except Exception as e:
            print(f"Monitor error: {e}")

    try:
        await telegram_client.run_until_disconnected()
    finally:
        TELEGRAM_MONITOR_RUNNING = False

@app.post("/telegram/start")
async def start_telegram(current=Depends(get_current_user)):
    global telegram_monitor_task, TELEGRAM_MONITOR_RUNNING
    if TELEGRAM_MONITOR_RUNNING: return {"status": "already running"}
    telegram_monitor_task = asyncio.create_task(run_telegram_monitor())
    return {"status": "starting"}

@app.post("/telegram/stop")
async def stop_telegram(current=Depends(get_current_user)):
    global telegram_client, TELEGRAM_MONITOR_RUNNING
    if telegram_client: await telegram_client.disconnect()
    TELEGRAM_MONITOR_RUNNING = False
    return {"status": "stopped"}

@app.get("/telegram/status")
async def get_telegram_status(current=Depends(get_current_user)):
    return {
        "running": TELEGRAM_MONITOR_RUNNING,
        "api_id": os.getenv("TELEGRAM_API_ID", "")[:5] + "...",
        "session_exists": os.path.exists(str(Path(__file__).resolve().parent / "session.session"))
    }


# ===========================  ENTRYPOINT  ===================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)