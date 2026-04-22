import numpy as np
import librosa
from .base import FingerprintModality

class AudioFingerprint(FingerprintModality):
    def extract(self, audio_path: str) -> np.ndarray:
        """
        Analyzes spectrogram peaks to identify unique sound signatures.
        """
        try:
            # Load audio (first 30 seconds)
            y, sr = librosa.load(audio_path, duration=30)
            
            # Compute Spectrogram
            S = np.abs(librosa.stft(y))
            
            # Extract MFCCs (Mel-frequency cepstral coefficients)
            # These are great for capturing unique audio signatures
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            
            # Flatten and sample to fit dimensionality
            sig = mfccs.mean(axis=1) # Average over time
            std = mfccs.std(axis=1)  # Variability over time
            
            combined = np.concatenate([sig, std])
            
            # Pad to 128
            if len(combined) < 128:
                combined = np.pad(combined, (0, 128 - len(combined)))
            else:
                combined = combined[:128]
                
            return combined.astype(np.float32)
        except Exception:
            # Fallback if audio fails
            return np.zeros(self.dimensionality, dtype=np.float32)

    @property
    def dimensionality(self) -> int:
        return 128
