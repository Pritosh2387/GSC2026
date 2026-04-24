import unittest
import os
import json
from ares.models import MatchMetadata, Platform, EnforcementCategory
from ares.engine import DecisionEngine, MockGeminiAdapter
from ares.ledger import EvidenceLedger

class TestARES(unittest.TestCase):
    def setUp(self):
        self.ai_adapter = MockGeminiAdapter()
        self.engine = DecisionEngine(self.ai_adapter)
        self.ledger_path = "test_ledger.json"
        self.ledger = EvidenceLedger(self.ledger_path)

    def tearDown(self):
        if os.path.exists(self.ledger_path):
            os.remove(self.ledger_path)

    def test_scoring_logic_takedown(self):
        """Verify that high-confidence piracy triggers a Takedown score (>0.85)."""
        match = MatchMetadata(
            match_id="TEST_001",
            content_id="HOT_FILM",
            match_confidence=1.0,
            transformation_index=1.0,
            view_velocity=5000.0,
            platform=Platform.YOUTUBE,
            uploader_id="pirate",
            uploader_reputation=0.0,
            jurisdiction="US",
            is_commercial=True
        )
        category, score, _ = self.engine.classify(match)
        self.assertGreater(score, 0.85)
        self.assertEqual(category, EnforcementCategory.TAKEDOWN)

    def test_scoring_logic_monitor(self):
        """Verify that transformative fan content triggers Monitor."""
        match = MatchMetadata(
            match_id="TEST_002",
            content_id="SONG",
            match_confidence=0.5,
            transformation_index=0.2, # Highly transformed
            view_velocity=10.0,
            platform=Platform.TIKTOK,
            uploader_id="fan",
            uploader_reputation=1.0,
            jurisdiction="US",
            is_commercial=False
        )
        category, score, _ = self.engine.classify(match)
        self.assertLess(score, 0.60)
        self.assertEqual(category, EnforcementCategory.MONITOR)

    def test_ledger_integrity(self):
        """Verify that the hash-chain link works correctly."""
        from ares.models import EnforcementAction
        from datetime import datetime
        
        # Log first action
        action1 = EnforcementAction(
            action_id="ACT1", match_id="M1", category=EnforcementCategory.MONITOR,
            severity_score=0.1, platform_response={}
        )
        hash1 = self.ledger.log_action(action1)
        
        # Log second action
        action2 = EnforcementAction(
            action_id="ACT2", match_id="M2", category=EnforcementCategory.TAKEDOWN,
            severity_score=0.9, platform_response={}
        )
        hash2 = self.ledger.log_action(action2)
        
        # Verify link
        with open(self.ledger_path, "r") as f:
            data = json.load(f)
            self.assertEqual(data[1]["previous_block_hash"], hash1)
            self.assertEqual(data[1]["blockchain_hash"], hash2)
        
        self.assertTrue(self.ledger.verify_integrity())

if __name__ == "__main__":
    unittest.main()
