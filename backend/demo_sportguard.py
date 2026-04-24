import numpy as np
from sportguard.orchestrator import SportGuardOrchestrator
from sportguard.fingerprinting.fusion import ContentType
from sportguard.attribution.response import OffenderType

def run_demo():
    print("="*60)
    print(" SportGuard AI: Multi-Layer Watermarking & Fingerprinting ")
    print("="*60)

    # 1. Initialize Orchestrator
    sg = SportGuardOrchestrator()

    # 2. Simulate Content Registration
    # (Using a dummy string as path since we are mocking the file processing logic for this demo)
    sg.register_content("live_premier_league_match.mp4", ContentType.LIVE_MATCH)

    # 3. Simulate Stream Protection for a User
    user_info = {
        "user_id": "user_88291",
        "device_id": "macbook_pro_m2",
        "tier": "premium",
        "region": "UK"
    }
    
    # Mock some frames and audio
    mock_frames = [np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8) for _ in range(20)]
    mock_audio = np.random.randn(44100)
    
    sg.protect_stream(mock_frames, mock_audio, user_info, 44100)

    # 4. Simulate Leak Attribution and Response
    print("\n--- SIMULATING LEAK SCENARIO ---")
    
    # Case: Commercial Scale Leaker
    sg.handle_leak_detection("pirated_stream.mp4", "pirated_audio.wav", OffenderType.COMMERCIAL_SCALE)

    # 5. Simulate Network Analysis (Feature 5)
    print("\n--- SIMULATING NETWORK DETECTION (CONTENT FARMS) ---")
    
    # Mock data for multiple accounts
    mock_fingerprints = {
        "account_alpha": np.random.randn(512),
        "account_beta": np.random.randn(512), 
        "account_gamma": np.zeros(512) + 0.100,  # Similar to Delta
        "account_delta": np.zeros(512) + 0.101   # Very Similar!
    }
    
    import time
    now = time.time()
    mock_logs = {
        "account_gamma": [now, now + 120, now + 240],
        "account_delta": [now + 1, now + 121, now + 241] # Coordinated!
    }
    
    sg.run_network_analysis(mock_fingerprints, mock_logs)

    print("\n" + "="*60)
    print(" DEMO COMPLETE ")
    print("="*60)

if __name__ == "__main__":
    run_demo()
