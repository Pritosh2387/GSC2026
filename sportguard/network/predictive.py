import numpy as np
from sklearn.ensemble import RandomForestClassifier
from typing import List, Dict

class PredictiveReplacementModel:
    """
    Identifies replacement accounts before they accumulate significant followers.
    """
    def __init__(self):
        # In a real system, this would be a pre-trained model
        self.model = RandomForestClassifier(n_estimators=100)
        self._is_trained = False

    def extract_features(self, account_meta: Dict) -> np.ndarray:
        """
        Extract features like registration time delta from takedown, 
        IP reuse, naming similarity, and initial upload patterns.
        """
        # Mock feature vector
        features = [
            account_meta.get("age_hours", 0),
            account_meta.get("shared_ip_count", 0),
            account_meta.get("naming_similarity", 0.0), # e.g., pirate_1 -> pirate_2
            account_meta.get("high_velocity_start", 0) # 1 if first hour has > 10 uploads
        ]
        return np.array(features).reshape(1, -1)

    def predict_replacement_risk(self, account_meta: Dict) -> float:
        """Returns risk score [0, 1]"""
        if not self._is_trained:
            # Heuristic fallback if not enough data to train
            risk = 0.0
            if account_meta.get("shared_ip_count", 0) > 0: risk += 0.4
            if account_meta.get("naming_similarity", 0) > 0.7: risk += 0.4
            if account_meta.get("high_velocity_start", 0): risk += 0.2
            return min(risk, 1.0)
            
        features = self.extract_features(account_meta)
        return float(self.model.predict_proba(features)[0][1])
