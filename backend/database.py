"""
database.py — MongoDB connection manager for SportGuard AI.

Uses motor (async MongoDB driver) for FastAPI compatibility.
Collections: alerts, matches, reference_fingerprints, users
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# Load .env from project root (one level up from backend/)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "sportguard")

client: Optional[AsyncIOMotorClient] = None
db = None


async def connect_to_mongo():
    """Initialize MongoDB connection on app startup."""
    global client, db
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[MONGODB_DB_NAME]
        # Verify connection
        await client.admin.command("ping")
        print(f"Connected to MongoDB: {MONGODB_DB_NAME}")

        # Create indexes
        await db.alerts.create_index([("timestamp", -1)])
        await db.alerts.create_index("severity")
        await db.alerts.create_index("resolved")
        await db.matches.create_index([("detected_at", -1)])
        await db.matches.create_index("similarity_score")
        await db.matches.create_index("file_hash", unique=True, sparse=True)
        await db.reference_fingerprints.create_index([("registered_at", -1)])
        await db.reference_fingerprints.create_index("media_type")
        await db.users.create_index("email", unique=True)
        print("MongoDB indexes created")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("   Falling back to JSON file storage.")


async def close_mongo():
    """Close MongoDB connection on app shutdown."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")


def get_db():
    """Return the database instance."""
    return db


def is_connected() -> bool:
    """Check if MongoDB is connected."""
    return db is not None
