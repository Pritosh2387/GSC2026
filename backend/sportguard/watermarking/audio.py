import numpy as np
import scipy.fftpack as fft

class AudioWatermark:
    """
    Modifies frequency spectra outside primary speech ranges.
    Subtle phase shifts in high-frequency bands encode user identifiers.
    """
    def __init__(self, freq_range=(16000, 20000)):
        self.freq_range = freq_range

    def embed(self, audio_data: np.ndarray, bit_sequence: np.ndarray, sr: int) -> np.ndarray:
        """
        Embeds bits via phase shifting in high frequencies.
        """
        # Compute FFT
        spectrum = fft.fft(audio_data)
        freqs = fft.fftfreq(len(audio_data), 1/sr)
        
        # Identity indices in target range
        idx = np.where((freqs >= self.freq_range[0]) & (freqs <= self.freq_range[1]))[0]
        
        # Apply phase shifts (simplified demonstration)
        # In reality, you'd use Echo Hiding or Phase Coding
        for i, bit in enumerate(bit_sequence):
            if i >= len(idx): break
            pos = idx[i]
            phase = np.angle(spectrum[pos])
            magnitude = np.abs(spectrum[pos])
            
            # Shift phase: 1 -> +pi/4, 0 -> -pi/4
            new_phase = phase + (np.pi/4 if bit == 1 else -np.pi/4)
            spectrum[pos] = magnitude * np.exp(1j * new_phase)
            # Maintain symmetry for real FFT
            spectrum[-pos] = np.conj(spectrum[pos])
            
        return fft.ifft(spectrum).real

    def extract(self, audio_data: np.ndarray, sr: int, expected_len: int) -> np.ndarray:
        """Recovers bits by analyzing phase differentials."""
        spectrum = fft.fft(audio_data)
        freqs = fft.fftfreq(len(audio_data), 1/sr)
        idx = np.where((freqs >= self.freq_range[0]) & (freqs <= self.freq_range[1]))[0]
        
        bits = []
        for i in range(min(len(idx), expected_len)):
            pos = idx[i]
            phase = np.angle(spectrum[pos])
            # Naive recovery: positive phase shift -> 1, negative -> 0
            bits.append(1 if phase > 0 else 0)
            
        return np.array(bits)
