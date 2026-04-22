import numpy as np

class TemporalWatermark:
    """
    Manipulates frame timing patterns imperceptibly.
    Micro-variations in frame durations encode binary sequences.
    """
    def __init__(self, fps=30):
        self.fps = fps
        self.base_duration = 1.0 / fps

    def calculate_frame_durations(self, bit_sequence: np.ndarray) -> np.ndarray:
        """
        Calculates the sequence of frame durations based on bits.
        '1' might be 1/30 + 0.001s, '0' might be 1/30 - 0.001s.
        """
        durations = []
        for bit in bit_sequence:
            # Shift by 1ms (imperceptible but detectable via jitter analysis)
            shift = 0.001 if bit == 1 else -0.001
            durations.append(self.base_duration + shift)
        return np.array(durations)

    def extract_from_jitters(self, arrival_times: np.ndarray) -> np.ndarray:
        """
        Extracts bits by analyzing inter-frame intervals.
        """
        intervals = np.diff(arrival_times)
        bits = []
        for interval in intervals:
            if interval > self.base_duration:
                bits.append(1)
            else:
                bits.append(0)
        return np.array(bits)
