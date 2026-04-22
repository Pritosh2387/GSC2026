from abc import ABC, abstractmethod
import numpy as np

class FingerprintModality(ABC):
    @abstractmethod
    def extract(self, content_path: str) -> np.ndarray:
        """Extract signature for this modality."""
        pass

    @property
    @abstractmethod
    def dimensionality(self) -> int:
        """Return the dimension of the resulting signature."""
        pass
