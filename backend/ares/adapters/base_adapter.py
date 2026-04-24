from abc import ABC, abstractmethod
from ..models import EnforcementCategory, MatchMetadata

class PlatformAdapter(ABC):
    @abstractmethod
    def execute_action(self, match: MatchMetadata, category: EnforcementCategory) -> dict:
        """
        Executes the enforcement action on the platform.
        Returns a dictionary containing the platform's response (e.g. claim_id, strike_id).
        """
        pass
