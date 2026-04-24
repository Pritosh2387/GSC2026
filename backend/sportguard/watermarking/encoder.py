import hashlib
import time
import struct

class WatermarkPayload:
    def __init__(self, user_id: str, device_id: str, tier: str, region: str):
        self.user_id = user_id
        self.device_id = device_id
        self.tier = tier
        self.region = region
        self.timestamp = int(time.time())

    def encode_128bit(self) -> bytes:
        """
        Encodes the metadata into a structured 128-bit payload.
        Fields: UserID (Hashed), Device Fingerprint, Tier, Timestamp, Region.
        """
        # Account Identifier (Hashed for privacy) - 32 bits
        user_hash = int(hashlib.md5(self.user_id.encode()).hexdigest(), 16) & 0xFFFFFFFF
        
        # Device Fingerprint (Hardware characteristics) - 32 bits
        device_hash = int(hashlib.md5(self.device_id.encode()).hexdigest(), 16) & 0xFFFFFFFF
        
        # Subscription Tier - 8 bits
        tier_map = {"basic": 1, "premium": 2, "ultra": 3}
        tier_val = tier_map.get(self.tier.lower(), 0)
        
        # Session Timestamp (last 32 bits of epoch)
        ts_val = self.timestamp & 0xFFFFFFFF
        
        # Geographic Region (Hashed) - 24 bits
        region_hash = int(hashlib.md5(self.region.encode()).hexdigest(), 16) & 0xFFFFFF
        region_bytes = region_hash.to_bytes(3, 'big')
        
        # Pack into 128 bits (16 bytes)
        # Total: 4 (I) + 4 (I) + 1 (B) + 4 (I) + 3 (3s) = 16 bytes
        payload = struct.pack(">IIBI3s", user_hash, device_hash, tier_val, ts_val, region_bytes)
        
        return payload

    @staticmethod
    def decode_128bit(payload: bytes) -> dict:
        """Decode the structured payload back to components."""
        if len(payload) != 16:
            return {"error": "Invalid payload length"}
            
        user_hash, device_hash, tier_val, ts_val, region_bytes = struct.unpack(">IIBI3s", payload)
        region_hash = int.from_bytes(region_bytes, 'big')
        return {
            "user_hash": hex(user_hash),
            "device_hash": hex(device_hash),
            "tier_indicator": tier_val,
            "session_ts": ts_val,
            "region_hash": hex(region_hash)
        }
