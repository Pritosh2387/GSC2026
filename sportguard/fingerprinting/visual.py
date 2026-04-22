import cv2
import numpy as np
from .base import FingerprintModality

class VisualFingerprint(FingerprintModality):
    def __init__(self, hash_size=16):
        self.hash_size = hash_size

    def extract(self, video_path: str) -> np.ndarray:
        """
        Extracts perceptual hashes from key frames using frequency domain analysis (DCT).
        """
        cap = cv2.VideoCapture(video_path)
        hashes = []
        
        # Strategy: Sample 10 keyframes spread across the video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0: return np.zeros(self.dimensionality)
        
        frame_indices = np.linspace(0, total_frames - 1, 10, dtype=int)
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret: continue
            
            # Perceptual Hashing using DCT
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
            
            # Apply 2D DCT
            dct = cv2.dct(np.float32(resized))
            
            # Extract top-left 8x8 (mid-frequencies)
            dct_low8 = dct[:8, :8]
            avg = dct_low8.mean()
            diff = dct_low8 > avg
            hashes.append(diff.flatten())
            
        cap.release()
        
        if not hashes:
            return np.zeros(self.dimensionality)
            
        # Flatten and normalize to expected dimensionality
        combined = np.concatenate(hashes).astype(np.float32)
        # Pad or truncate to 128 (let's say 128 for visual)
        if len(combined) > 128:
            combined = combined[:128]
        else:
            combined = np.pad(combined, (0, 128 - len(combined)))
            
        return combined

    @property
    def dimensionality(self) -> int:
        return 128
