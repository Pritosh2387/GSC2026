import json
import hashlib
import os
from datetime import datetime
from typing import List, Optional
from .models import EnforcementAction

class EvidenceLedger:
    def __init__(self, storage_path: str = "ares_ledger.json"):
        self.storage_path = storage_path
        self.ledger: List[dict] = self._load_ledger()

    def _load_ledger(self) -> List[dict]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _get_last_hash(self) -> str:
        if not self.ledger:
            return "0" * 64  # Genesis block hash
        return self.ledger[-1].get("blockchain_hash", "0" * 64)

    def log_action(self, action: EnforcementAction) -> str:
        """
        Logs an enforcement action and returns the new block hash.
        Each block is chained to the previous one using SHA-256.
        """
        previous_hash = self._get_last_hash()
        action.previous_block_hash = previous_hash
        
        # Prepare data for hashing
        block_data = {
            "action_id": action.action_id,
            "match_id": action.match_id,
            "category": action.category,
            "timestamp": action.timestamp.isoformat(),
            "previous_hash": previous_hash
        }
        
        # Calculate current hash
        block_string = json.dumps(block_data, sort_keys=True).encode()
        current_hash = hashlib.sha256(block_string).hexdigest()
        
        action.blockchain_hash = current_hash
        
        # Store in local JSON
        self.ledger.append(action.model_dump(mode='json'))
        self._save()
        
        return current_hash

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.ledger, f, indent=4)

    def verify_integrity(self) -> bool:
        """
        Verifies that the hash chain is unbroken.
        """
        if not self.ledger:
            return True
        
        for i in range(1, len(self.ledger)):
            current = self.ledger[i]
            previous = self.ledger[i-1]
            
            # Recalculate what the previous block's hash should have been if we were verifying the whole thing
            # For this simple mock, we just check the link
            if current["previous_block_hash"] != previous["blockchain_hash"]:
                return False
        return True
