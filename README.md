# SportGuard AI: Advanced Anti-Piracy Protection

SportGuard AI is a comprehensive security suite designed to protect live sports broadcasts and premium content from unauthorized distribution. It combines individual stream protection with large-scale network detection.

---

## Key Features

### 1. Multi-Layer Fingerprinting
Uses four parallel modalities to create a 512-dimensional fused signature:
- **Visual**: Freq-domain analysis (DCT) of keyframes.
- **Audio**: Spectrogram and MFCC characteristic extraction.
- **Temporal**: Mapping scene-change sequences.
- **Semantic**: Gemini AI-driven descriptions of on-screen events.

### 2. Forensic Watermarking
Invisible session-specific watermarking across three domains:
- **Luminance**: DCT mid-frequency coefficient adjustment.
- **Temporal**: Imperceptible frame-timing jitter.
- **Audio**: Phase shifting in high-frequency bands.
- **Payload**: 128-bit structured payload (User, Device, Tier, TS, Region).

### 3. Content Farm & Network Detection
Moves beyond individual leaks to dismantle piracy organizations:
- **Knowledge Graph**: Maps relationships between accounts, IPs, devices, and payments.
- **Pattern Recognition**:
  - **Upload Velocity**: Detects automated posting.
  - **Similarity Clustering**: Groups accounts via shared fingerprints.
  - **Temporal Coordination**: Detects coordinated activity.
- **Predictive Replacements**: ML models identify new accounts replacing banned ones.

---

## Modular Architecture

- `sportguard/fingerprinting/`: Content identification engines  
- `sportguard/watermarking/`: Forensic embedding pipelines  
- `sportguard/network/`: Graph analytics and detection  
- `sportguard/attribution/`: Enforcement and legal evidence  

---

## Getting Started
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install opencv-python librosa scipy numpy networkx pandas scikit-learn
   ```
3. Run the demonstration:
   ```bash
   python demo_sportguard.py
   ```

## Automated Response Protocol
- **First-time**: Warning and educational content.
- **Repeat**: Temporary suspension.
- **Commercial Scale**: Permanent termination, evidence preservation, and law enforcement referral.
