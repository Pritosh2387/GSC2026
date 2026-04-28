"""
main.py — PIRAKSHA API entry point.

PIRAKSHA: AI-Powered Media Piracy Detection System
===================================================

Startup:
    uvicorn main:app --reload --port 8000

Swagger UI:
    http://127.0.0.1:8000/docs

ReDoc:
    http://127.0.0.1:8000/redoc

All route modules are registered under /api/* prefixes.
"""

import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

# ── Bootstrap path so all existing backend modules are importable ─────────────
# config.py adds backend/ to sys.path when imported
from config import settings  # noqa: E402 (import after sys.path manipulation)
from database import connect_to_mongo, close_mongo
from utils.logging_utils import get_logger

logger = get_logger("piraksha.main")

# ── Deepfake model: attempt pre-load at startup ───────────────────────────────
from services.deepfake_service import load_model as _load_deepfake_model


# ── Lifespan (modern FastAPI startup / shutdown) ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic for PIRAKSHA API."""
    # ── STARTUP ───────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("  PIRAKSHA API  —  Starting up")
    logger.info("=" * 60)

    await connect_to_mongo()

    try:
        loaded = _load_deepfake_model()
        if loaded:
            logger.info("Deepfake CNN-LSTM model loaded successfully.")
        else:
            logger.warning("Deepfake model not available (TF/OpenCV missing or model file absent).")
    except Exception as exc:
        logger.warning(f"Deepfake model load skipped: {exc}")

    logger.info(f"Docs available at: http://127.0.0.1:8000{settings.DOCS_URL}")
    logger.info("PIRAKSHA API is ready.")

    yield  # ← Application runs here

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────
    logger.info("PIRAKSHA API shutting down...")
    await close_mongo()

    from services.telegram_service import stop_monitor, MONITOR_RUNNING
    if MONITOR_RUNNING:
        await stop_monitor()
    logger.info("Shutdown complete.")

# ── FastAPI application ───────────────────────────────────────────────────────
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    lifespan=lifespan,
    contact={
        "name": "PIRAKSHA Team",
        "url": "https://github.com/Pritosh2387/GSC2026",
    },
    license_info={
        "name": "MIT",
    },
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler — logs the full traceback and returns a clean JSON error."""
    logger.error(
        f"Unhandled exception on {request.method} {request.url}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url),
        },
    )


# (Lifecycle is now handled by the lifespan context manager above)


# ── Health / root endpoints ───────────────────────────────────────────────────
@app.get(
    "/",
    tags=["Health"],
    summary="Root health check",
    description="Returns system status and API metadata.",
)
async def root():
    """PIRAKSHA API root — confirms the service is alive."""
    from database import is_connected
    from services.deepfake_service import _model as _df_model
    from services.telegram_service import MONITOR_RUNNING

    return {
        "service": "PIRAKSHA API",
        "version": settings.API_VERSION,
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "capabilities": {
            "database_connected": is_connected(),
            "deepfake_model_loaded": _df_model is not None,
            "telegram_monitor_running": MONITOR_RUNNING,
        },
        "docs": f"http://127.0.0.1:8000{settings.DOCS_URL}",
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
)
async def health():
    """Lightweight health-check for load balancers / k8s probes."""
    from database import is_connected
    return {
        "status": "ok",
        "database": "connected" if is_connected() else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Register all route modules ────────────────────────────────────────────────
from routes.auth import router as auth_router
from routes.fingerprint import router as fingerprint_router
from routes.watermark import router as watermark_router
from routes.telegram import router as telegram_router
from routes.detection import router as detection_router
from routes.deepfake import router as deepfake_router
from routes.network import router as network_router
from routes.enforcement import router as enforcement_router
from routes.analytics import router as analytics_router
from routes.alerts import router as alerts_router

app.include_router(auth_router)
app.include_router(fingerprint_router)
app.include_router(watermark_router)
app.include_router(telegram_router)
app.include_router(detection_router)
app.include_router(deepfake_router)
app.include_router(network_router)
app.include_router(enforcement_router)
app.include_router(analytics_router)
app.include_router(alerts_router)


# ── Custom OpenAPI schema ─────────────────────────────────────────────────────
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description=settings.API_DESCRIPTION,
        routes=app.routes,
    )
    schema["info"]["x-logo"] = {"url": "https://piraksha.ai/logo.png"}
    schema["tags"] = [
        {"name": "Health",                 "description": "System health and status"},
        {"name": "Authentication",          "description": "User registration and JWT login"},
        {"name": "Media & Watermark",       "description": "Original media registration and forensic watermarking"},
        {"name": "Fingerprint",             "description": "Perceptual fingerprint generation and comparison"},
        {"name": "Telegram Monitor",        "description": "Background Telegram channel surveillance"},
        {"name": "Detection",               "description": "End-to-end piracy detection pipeline"},
        {"name": "Deepfake Detection",      "description": "CNN-LSTM deepfake video analysis"},
        {"name": "Network Propagation",     "description": "Piracy propagation graph and coordinated-network detection"},
        {"name": "Enforcement",             "description": "ARES enforcement engine and blockchain evidence ledger"},
        {"name": "Analytics",              "description": "Dashboard metrics and reporting"},
    ]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


# ── Dev entrypoint ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )
