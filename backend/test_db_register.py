
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Path setup
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import connect_to_mongo, get_db
from auth import hash_password

async def test_register():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    await connect_to_mongo()
    db = get_db()
    if db is None:
        print("DB is None!")
        return

    try:
        user_doc = {
            "name": "Test User",
            "email": "test@test.com",
            "password_hash": hash_password("password123"),
            "created_at": "now"
        }
        result = await db.users.insert_one(user_doc)
        print(f"User inserted: {result.inserted_id}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_register())
