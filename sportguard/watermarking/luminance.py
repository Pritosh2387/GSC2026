import cv2
import numpy as np

class LuminanceWatermark:
    def __init__(self, block_size=8, alpha=0.1):
        self.block_size = block_size
        self.alpha = alpha # Strength of watermark

    def embed(self, frame: np.ndarray, bit_sequence: np.ndarray) -> np.ndarray:
        """
        Embeds bits into luminance domain using DCT.
        Modifies mid-frequency coefficients of 8x8 blocks.
        """
        # Convert to YUV to separate luminance
        yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
        Y = yuv[:, :, 0].astype(np.float32)
        
        h, w = Y.shape
        bit_idx = 0
        
        for i in range(0, h - self.block_size, self.block_size):
            for j in range(0, w - self.block_size, self.block_size):
                if bit_idx >= len(bit_sequence):
                    break
                
                block = Y[i:i+self.block_size, j:j+self.block_size]
                dct_block = cv2.dct(block)
                
                # Mid-frequency coefficient (e.g., [4,4])
                bit = bit_sequence[bit_idx]
                # Simple Spread Spectrum or Quantization Index Modulation
                # Here we use a simpler version: slightly shift a mid-freq coefficient
                # based on the bit value
                target_coeff = (4, 4)
                if bit == 1:
                    dct_block[target_coeff] += self.alpha * 10
                else:
                    dct_block[target_coeff] -= self.alpha * 10
                    
                Y[i:i+self.block_size, j:j+self.block_size] = cv2.idct(dct_block)
                bit_idx += 1
                
        yuv[:, :, 0] = np.clip(Y, 0, 255).astype(np.uint8)
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    def extract(self, frame: np.ndarray, expected_len: int) -> np.ndarray:
        """Recover bits from luminance domain."""
        yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
        Y = yuv[:, :, 0].astype(np.float32)
        
        h, w = Y.shape
        bits = []
        bit_idx = 0
        
        for i in range(0, h - self.block_size, self.block_size):
            for j in range(0, w - self.block_size, self.block_size):
                if bit_idx >= expected_len:
                    break
                
                block = Y[i:i+self.block_size, j:j+self.block_size]
                dct_block = cv2.dct(block)
                
                # Check the coefficient value (very naive recovery for demonstration)
                val = dct_block[4, 4]
                bits.append(1 if val > 0 else 0)
                bit_idx += 1
                
        return np.array(bits)
