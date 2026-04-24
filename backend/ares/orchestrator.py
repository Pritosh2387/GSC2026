import uuid
from datetime import datetime
from typing import Dict
from .models import MatchMetadata, EnforcementAction, Platform
from .engine import DecisionEngine
from .ledger import EvidenceLedger
from .adapters.youtube_adapter import YouTubeAdapter
from .adapters.meta_adapter import MetaAdapter
from .adapters.tiktok_adapter import TikTokAdapter

class AresOrchestrator:
    def __init__(self, engine: DecisionEngine, ledger: EvidenceLedger):
        self.engine = engine
        self.ledger = ledger
        self.adapters = {
            Platform.YOUTUBE: YouTubeAdapter(),
            Platform.META: MetaAdapter(),
            Platform.TIKTOK: TikTokAdapter()
        }

    def process_match(self, match: MatchMetadata) -> EnforcementAction:
        print(f"[*] Processing Match {match.match_id} on {match.platform.value}...")
        
        # 1. Decision Engine Logic (includes AI Analysis)
        category, score, ai_context = self.engine.classify(match)
        print(f"    - Action Severity Score: {score}")
        print(f"    - Decision: {category.value.upper()}")
        print(f"    - AI Reasoning: {ai_context['reasoning']}")

        # 2. Platform Action Execution
        adapter = self.adapters.get(match.platform)
        if not adapter:
            raise ValueError(f"No adapter found for platform {match.platform}")
        
        platform_response = adapter.execute_action(match, category)
        print(f"    - Platform Action: {platform_response.get('internal_logic', 'executed')}")

        # 3. Create Enforcement Action Record
        action = EnforcementAction(
            action_id=f"ACT_{uuid.uuid4().hex[:8].upper()}",
            match_id=match.match_id,
            category=category,
            severity_score=score,
            platform_response=platform_response
        )

        # 4. Log to Immutable Ledger (Blockchain Simulation)
        block_hash = self.ledger.log_action(action)
        print(f"    - Blockchain Proof: {block_hash[:16]}...")
        
        return action
