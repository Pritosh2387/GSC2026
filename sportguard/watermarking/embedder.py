import numpy as np
from .encoder import WatermarkPayload
from .luminance import LuminanceWatermark
from .temporal import TemporalWatermark
from .audio import AudioWatermark

class WatermarkEmbedder:
    def __init__(self):
        self.lum_engine = LuminanceWatermark()
        self.temp_engine = TemporalWatermark()
        self.aud_engine = AudioWatermark()

    def apply_watermark(self, video_frames: list, audio_samples: np.ndarray, 
                       user_info: dict, sr: int) -> tuple:
        """
        Applies a multi-domain watermark to a user stream.
        """
        payload_gen = WatermarkPayload(
            user_id=user_info["user_id"],
            device_id=user_info["device_id"],
            tier=user_info["tier"],
            region=user_info["region"]
        )
        payload_bytes = payload_gen.encode_128bit()
        
        # Convert bytes to bit array
        bits = np.unpackbits(np.frombuffer(payload_bytes, dtype=np.uint8))
        
        # 1. Embed in Luminance (apply to every 10th frame for efficiency/redundancy)
        watermarked_frames = []
        for i, frame in enumerate(video_frames):
            if i % 10 == 0:
                frame = self.lum_engine.embed(frame, bits)
            watermarked_frames.append(frame)
            
        # 2. Embed in Audio
        watermarked_audio = self.aud_engine.embed(audio_samples, bits, sr)
        
        # 3. Calculate Jitters (for downstream player)
        jitters = self.temp_engine.calculate_frame_durations(bits)
        
        return watermarked_frames, watermarked_audio, jitters
