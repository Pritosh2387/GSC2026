import cv2
import numpy as np
from .base import FingerprintModality

class TemporalFingerprint(FingerprintModality):
    def extract(self, video_path: str) -> np.ndarray:
        """
        Maps scene change sequences to create unique temporal signatures.
        """
        cap = cv2.VideoCapture(video_path)
        last_frame = None
        scene_changes = []
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            # Simple frame difference for scene detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            if last_frame is not None:
                diff = cv2.absdiff(last_frame, gray)
                score = np.mean(diff)
                scene_changes.append(score)
            
            last_frame = gray
            
            # Optimization: skip frames to speed up analysis
            for _ in range(24): # skip 1 second if 24fps
                cap.grab()
                
        cap.release()
        
        # Normalize scene change sequence to 128 dimensions
        signature = np.array(scene_changes, dtype=np.float32)
        if len(signature) < 128:
            signature = np.pad(signature, (0, 128 - len(signature)))
        else:
            # Resample to 128
            indices = np.linspace(0, len(signature)-1, 128).astype(int)
            signature = signature[indices]
            
        # Normalize
        if np.max(signature) > 0:
            signature = signature / np.max(signature)
            
        return signature

    @property
    def dimensionality(self) -> int:
        return 128
