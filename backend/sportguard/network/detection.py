import pandas as pd
import numpy as np
from typing import List, Dict

class NetworkDetectionSystem:
    def __init__(self, kg):
        self.kg = kg

    def detect_high_velocity_uploads(self, user_id: str, upload_timestamps: List[float]) -> bool:
        """
        Indicator: Posting faster than humanly possible.
        Method: Sequential timestamp analysis.
        """
        if len(upload_timestamps) < 2: return False
        
        diffs = np.diff(sorted(upload_timestamps))
        # Threshold: More than 5 uploads with 10s gap is suspicious of automation
        suspicious_burst = np.sum(diffs < 10) > 5
        return suspicious_burst

    def find_content_similarity_clusters(self, fingerprint_map: Dict[str, np.ndarray]) -> List[List[str]]:
        """
        Indicator: Near-identical uploads across multiple accounts.
        Method: Perceptual hashing clustering (L2 distance thresholding).
        """
        uids = list(fingerprint_map.keys())
        features = np.array(list(fingerprint_map.values()))
        
        clusters = []
        visited = set()
        
        for i, uid in enumerate(uids):
            if uid in visited: continue
            
            # Find all users with similarity > 0.95
            current_cluster = [uid]
            visited.add(uid)
            
            for j in range(i + 1, len(uids)):
                dist = np.linalg.norm(features[i] - features[j])
                if dist < 0.1: # Very close in 512-dim normalized space
                    current_cluster.append(uids[j])
                    visited.add(uids[j])
            
            if len(current_cluster) > 1:
                clusters.append(current_cluster)
                
        return clusters

    def analyze_temporal_coordination(self, account_logs: Dict[str, List[float]]) -> List[str]:
        """
        Indicator: Scheduled posting patterns (Coordinated Upload Timing).
        Method: Time-series cross-correlation or peak alignment.
        """
        coordinated_accounts = []
        uids = list(account_logs.keys())
        
        for i in range(len(uids)):
            for j in range(i + 1, len(uids)):
                # Simple check: do they upload within 60s of each other consistently?
                logs_a = sorted(account_logs[uids[i]])
                logs_b = sorted(account_logs[uids[j]])
                
                matches = 0
                for ts_a in logs_a:
                    for ts_b in logs_b:
                        if abs(ts_a - ts_b) < 60:
                            matches += 1
                            break
                
                if matches > 3: # Threshold for coordination
                    coordinated_accounts.extend([uids[i], uids[j]])
                    
        return list(set(coordinated_accounts))
