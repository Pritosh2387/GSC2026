from ares.models import MatchMetadata, Platform
from ares.engine import DecisionEngine, MockGeminiAdapter
from ares.ledger import EvidenceLedger
from ares.orchestrator import AresOrchestrator
import time

def run_simulations():
    print("="*60)
    print(" ARES: Automated Revenue Enforcement & Shield - Pipeline Simulation")
    print("="*60)

    # Initialize Components
    ai_adapter = MockGeminiAdapter()
    engine = DecisionEngine(ai_adapter)
    ledger = EvidenceLedger("ares_ledger.json")
    orchestrator = AresOrchestrator(engine, ledger)

    # Scenario 1: High-Confidence Viral Piracy (Exact Copy)
    match1 = MatchMetadata(
        match_id="M_ID_9921",
        content_id="BLOCKBUSTER_FILM_2024",
        match_confidence=1.0,  # Exact match
        transformation_index=1.0, # RAW re-upload
        view_velocity=5000.0, # Viral velocity
        platform=Platform.YOUTUBE,
        uploader_id="pirate_bay_official",
        uploader_reputation=0.1, # Known bad actor
        jurisdiction="RU",
        is_commercial=True
    )

    # Scenario 2: Fan Edit (Transformative)
    match2 = MatchMetadata(
        match_id="M_ID_8832",
        content_id="LATEST_SINGLE_MTV",
        match_confidence=0.75, 
        transformation_index=0.3, # Highly edited
        view_velocity=250.0,
        platform=Platform.TIKTOK,
        uploader_id="fan_dancer_01",
        uploader_reputation=0.9,
        jurisdiction="US",
        is_commercial=False
    )

    # Scenario 3: Micro-Commercial Use (Small Scale Infringement)
    match3 = MatchMetadata(
        match_id="M_ID_7743",
        content_id="STOCK_FOOTAGE_CITY",
        match_confidence=0.9,
        transformation_index=0.7,
        view_velocity=10.0, # Low velocity
        platform=Platform.META,
        uploader_id="small_biz_owner",
        uploader_reputation=1.0, # Clean history
        jurisdiction="UK",
        is_commercial=True
    )

    scenarios = [match1, match2, match3]

    for i, match in enumerate(scenarios, 1):
        print(f"\n[Scenario {i}: {match.content_id}]")
        orchestrator.process_match(match)
        time.sleep(1)

    print("\n" + "="*60)
    print(" SIMULATION COMPLETE")
    print(f" Ledger Integrity Verified: {ledger.verify_integrity()}")
    print("="*60)

if __name__ == "__main__":
    run_simulations()
