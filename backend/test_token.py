
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Path setup
sys.path.insert(0, str(Path(__file__).resolve().parent))

from auth import create_access_token

def test_token():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    try:
        token = create_access_token({"sub": "test", "email": "test@test.com"})
        print(f"Token created: {token[:20]}...")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_token()
