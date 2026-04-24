"""
generate_reference_db.py

Creates reference fingerprints from media files.
These fingerprints are later used for matching.
"""

import os
import json
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Ensure project root import works
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from telegram.telegram_utils import (
    fingerprint_image,
    fingerprint_video,
    get_media_type,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# Folder containing reference media
REFERENCE_FOLDER = os.path.join(
    PROJECT_ROOT,
    "reference_media"
)

# Output fingerprint database
REFERENCE_DB_PATH = os.path.join(
    PROJECT_ROOT,
    "reference_fingerprints.json"
)


# ---------------------------------------------------------------------------
# Main Function
# ---------------------------------------------------------------------------

def main():

    if not os.path.exists(REFERENCE_FOLDER):
        print("❌ reference_media folder not found!")
        return

    reference_entries = []

    files = os.listdir(REFERENCE_FOLDER)

    if not files:
        print("❌ No files inside reference_media/")
        return

    print(f"🔍 Processing {len(files)} reference files...")

    for file_name in files:

        file_path = os.path.join(
            REFERENCE_FOLDER,
            file_name
        )

        media_type = get_media_type(file_path)

        if media_type is None:
            print(f"⏭️ Skipping unsupported file: {file_name}")
            continue

        print(f"📄 Processing: {file_name}")

        # Generate fingerprint
        if media_type == "image":
            fingerprint = fingerprint_image(file_path)
        else:
            fingerprint = fingerprint_video(file_path)

        if fingerprint is None:
            print(f"⚠️ Failed to fingerprint {file_name}")
            continue

        # ✅ FULL schema — matches ReferenceDatabase expectations
        entry = {
            "content_name": file_name,
            "content_path": file_path,
            "media_type": media_type,
            "fingerprint": fingerprint.tolist(),
            "dimension": len(fingerprint),
            "registered_at": datetime.now().isoformat()
        }

        reference_entries.append(entry)

    # Save database
    with open(REFERENCE_DB_PATH, "w") as f:
        json.dump(reference_entries, f, indent=4)

    print(
        f"✅ Saved {len(reference_entries)} reference fingerprints!"
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()