import numpy as np
from enum import Enum

class ContentType(Enum):
    LIVE_MATCH = "live_match"
    HIGHLIGHT_REEL = "highlight_reel"
    GENERAL = "general"

class FingerprintFusion:
    def __init__(self):
        # Weights for normalization and importance
        self.weights = {
            ContentType.LIVE_MATCH: {
                "visual": 0.2,
                "audio": 0.4,
                "temporal": 0.3,
                "semantic": 0.1
            },
            ContentType.HIGHLIGHT_REEL: {
                "visual": 0.4,
                "audio": 0.1,
                "temporal": 0.2,
                "semantic": 0.3
            },
            ContentType.GENERAL: {
                "visual": 0.25,
                "audio": 0.25,
                "temporal": 0.25,
                "semantic": 0.25
            }
        }

    def fuse(self, visual_sig, audio_sig, temporal_sig, semantic_sig, content_type: ContentType) -> np.ndarray:
        """
        Fuses four modalities into a 512-dimensional vector representation.
        Applies learned weights based on content type.
        """
        w = self.weights.get(content_type, self.weights[ContentType.GENERAL])
        
        # Apply weights to each sub-signature
        visual_weighted = visual_sig * w["visual"]
        audio_weighted = audio_sig * w["audio"]
        temporal_weighted = temporal_sig * w["temporal"]
        semantic_weighted = semantic_sig * w["semantic"]
        
        # Concatenate into 512-dim vector
        fused = np.concatenate([
            visual_weighted,
            audio_weighted,
            temporal_weighted,
            semantic_weighted
        ])
        
        # Final L2 normalization
        norm = np.linalg.norm(fused)
        if norm > 0:
            fused = fused / norm
            
        return fused
