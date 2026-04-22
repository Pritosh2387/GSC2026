import numpy as np
import tensorflow as tf
from fastapi import FastAPI, UploadFile, File
import uvicorn
import cv2
import tempfile
import os

from keras.layers import Dense

original_init = Dense.__init__

def new_init(self, *args, **kwargs):
    kwargs.pop("quantization_config", None)
    original_init(self, *args, **kwargs)

Dense.__init__ = new_init

app = FastAPI(title="CNN-LSTM Video Classification API")

MODEL_PATH = "cnn_lstm_new_model.keras"

print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
print("Model loaded successfully!")

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
    return {"message": " CNN-LSTM Video API is running"}

@app.post("/predict-video")
async def predict_video(file: UploadFile = File(...)):
    temp_path = None

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

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)