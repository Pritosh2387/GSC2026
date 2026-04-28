"""
models/user_model.py — Pydantic request / response schemas for authentication.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    """Request body for POST /api/register."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

    model_config = {"json_schema_extra": {"example": {
        "name": "Aanya Sharma",
        "email": "aanya@piraksha.ai",
        "password": "secure123",
    }}}


class UserLogin(BaseModel):
    """Request body for POST /api/login."""
    email: EmailStr
    password: str

    model_config = {"json_schema_extra": {"example": {
        "email": "aanya@piraksha.ai",
        "password": "secure123",
    }}}


class UserResponse(BaseModel):
    """Returned user object (no password field)."""
    id: str
    name: str
    email: str
    created_at: str


class TokenResponse(BaseModel):
    """JWT access-token envelope."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
