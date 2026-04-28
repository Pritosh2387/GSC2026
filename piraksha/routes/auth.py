"""
routes/auth.py — Authentication endpoints.

POST /api/register  — Create a new user account, return JWT
POST /api/login     — Authenticate, return JWT
GET  /api/me        — Return current user profile (protected)
"""

import uuid
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, status

from database import get_db
from models.user_model import UserCreate, UserLogin, UserResponse, TokenResponse
from utils.logging_utils import get_logger

# Re-use the well-tested auth helpers from the backend folder
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api", tags=["Authentication"])
logger = get_logger("piraksha.routes.auth")


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Create a new PIRAKSHA user account. "
        "Returns a JWT access token and the created user profile."
    ),
)
async def register(user: UserCreate):
    """
    **Register** a new user account.

    - Checks for duplicate email
    - Hashes password using PBKDF2-SHA256
    - Creates user document in MongoDB
    - Returns a signed JWT bearer token
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "name": user.name,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "created_at": now,
        "role": "analyst",
    }
    result = await db.users.insert_one(doc)
    uid = str(result.inserted_id)

    token = create_access_token({"sub": uid, "email": user.email})
    logger.info(f"User registered: {user.email} ({uid})")
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=uid, name=user.name, email=user.email, created_at=now),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate with email and password. Returns a JWT bearer token.",
)
async def login(creds: UserLogin):
    """
    **Login** with email and password.

    Returns a JWT access token valid for 24 hours (configurable via env).
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    user = await db.users.find_one({"email": creds.email})
    if not user or not verify_password(creds.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    uid = str(user["_id"])
    token = create_access_token({"sub": uid, "email": user["email"]})
    logger.info(f"User logged in: {creds.email}")
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=uid,
            name=user["name"],
            email=user["email"],
            created_at=user.get("created_at", ""),
        ),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Return the profile of the currently authenticated user.",
)
async def me(current=Depends(get_current_user)):
    """Return authenticated user's profile.  Requires valid Bearer token."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    user = await db.users.find_one({"_id": ObjectId(current["user_id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user.get("created_at", ""),
    )
