import numpy as np
from ..watermarking.encoder import WatermarkPayload
from ..watermarking.luminance import LuminanceWatermark
from ..watermarking.audio import AudioWatermark

class AttributionWorkflow:
    def __init__(self):
        self.lum_extractor = LuminanceWatermark()
        self.aud_extractor = AudioWatermark()

    def attribute_leak(self, suspect_video_path: str, suspect_audio_path: str) -> dict:
        """
        Leak Attribution Workflow:
        1. Forensic extraction from multiple domains
        2. Recovery of original user session identifier
        3. Correlation with account logs
        """
        # Mocking extraction results
        # In a real system, we'd process the video/audio files
        bits_recovered = []
        
        # Try Luminance
        lum_bits = np.random.randint(0, 2, 128) # Simulated recovery
        bits_recovered.append(lum_bits)
        
        # Try Audio
        aud_bits = np.random.randint(0, 2, 128) # Simulated recovery
        bits_recovered.append(aud_bits)
        
        # Error recovery (Majority Voting across domains)
        fused_bits = self._majority_vote(bits_recovered)
        
        # Convert bits back to bytes
        payload_bytes = np.packbits(fused_bits).tobytes()
        
        # Decode components
        attribution_data = WatermarkPayload.decode_128bit(payload_bytes)
        
        return attribution_data

    def _majority_vote(self, list_of_bitarrays):
        if not list_of_bitarrays: return np.zeros(128, dtype=int)
        arr = np.stack(list_of_bitarrays)
        return (np.mean(arr, axis=0) > 0.5).astype(int)
