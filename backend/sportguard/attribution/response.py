from enum import Enum
import json
import os

class OffenderType(Enum):
    FIRST_TIME = "first_time"
    REPEAT = "repeat"
    COMMERCIAL_SCALE = "commercial_scale"

class ResponseProtocol:
    def __init__(self, preservation_dir: str):
        self.preservation_dir = preservation_dir
        if not os.path.exists(preservation_dir):
            os.makedirs(preservation_dir)

    def execute_response(self, user_id: str, offender_type: OffenderType, evidence_data: dict):
        """
        Executes automated response based on offender type.
        """
        if offender_type == OffenderType.FIRST_TIME:
            return self._warning_response(user_id)
        elif offender_type == OffenderType.REPEAT:
            return self._suspension_response(user_id)
        elif offender_type == OffenderType.COMMERCIAL_SCALE:
            return self._termination_response(user_id, evidence_data)

    def _warning_response(self, user_id):
        print(f"DEBUG: Issued WARNING to user {user_id}. Sending educational content.")
        return {"action": "warning", "user": user_id}

    def _suspension_response(self, user_id):
        print(f"DEBUG: Issued TEMPORARY SUSPENSION to user {user_id}.")
        return {"action": "suspension", "user": user_id}

    def _termination_response(self, user_id, evidence_data):
        print(f"DEBUG: PERMANENT TERMINATION for user {user_id}. Preserving evidence.")
        
        # Evidence preservation for legal action
        evidence_file = os.path.join(self.preservation_dir, f"evidence_{user_id}_{evidence_data['session_ts']}.json")
        with open(evidence_file, "w") as f:
            json.dump({
                "user_id": user_id,
                "offender_type": "COMMERCIAL_SCALE",
                "evidence": evidence_data
            }, f, indent=4)
            
        return {"action": "termination", "user": user_id, "evidence_preserved": True}
