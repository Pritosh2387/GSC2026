import gdown
import tensorflow as tf
import os

FILE_ID = "1o_jinpmPFLad1iGhAyapBbtpUT39d7Hy"

MODEL_PATH = "/content/cnn_lstm_new_model.keras"

URL = f"https://drive.google.com/uc?id={FILE_ID}"

# Force download if file not present OR corrupted
if not os.path.exists(MODEL_PATH) or os.path.getsize(MODEL_PATH) < 10_000:
    print("Downloading model...")

    gdown.download(
        URL,
        MODEL_PATH,
        quiet=False,
        fuzzy=True   # IMPORTANT FIX (handles Drive links better)
    )

# Validate file after download
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Download failed: file not created")

if os.path.getsize(MODEL_PATH) < 10_000:
    raise ValueError("Downloaded file is corrupted or incomplete")

print("Loading model...")

model = tf.keras.models.load_model(MODEL_PATH, compile=False)

print("Model loaded successfully")
