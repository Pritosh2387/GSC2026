import concurrent.futures
from typing import Dict
import numpy as np
from .visual import VisualFingerprint
from .audio import AudioFingerprint
from .temporal import TemporalFingerprint
from .semantic import SemanticFingerprint
from .fusion import FingerprintFusion, ContentType

class FingerprintingEngine:
    def __init__(self, gemini_api_key: str = None):
        self.visual_engine = VisualFingerprint()
        self.audio_engine = AudioFingerprint()
        self.temporal_engine = TemporalFingerprint()
        self.semantic_engine = SemanticFingerprint(gemini_api_key)
        self.fusion_engine = FingerprintFusion()

    def generate_fingerprint(self, content_path: str, content_type: ContentType = ContentType.GENERAL) -> np.ndarray:
        """
        Orchestrates parallel extraction of all four modality signatures and fuses them.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Launch extraction tasks in parallel
            future_visual = executor.submit(self.visual_engine.extract, content_path)
            future_audio = executor.submit(self.audio_engine.extract, content_path)
            future_temporal = executor.submit(self.temporal_engine.extract, content_path)
            future_semantic = executor.submit(self.semantic_engine.extract, content_path)

            # Gather results
            visual_sig = future_visual.result()
            audio_sig = future_audio.result()
            temporal_sig = future_temporal.result()
            semantic_sig = future_semantic.result()

        # Fuse into 512-dim vector
        return self.fusion_engine.fuse(visual_sig, audio_sig, temporal_sig, semantic_sig, content_type)
