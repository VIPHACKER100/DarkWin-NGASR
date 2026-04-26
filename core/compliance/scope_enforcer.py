import json
from core.logging_system import get_logger

logger = get_logger("Compliance.ScopeEnforcer")

class ScopeEnforcer:
    def __init__(self, scope_file: str):
        self.scope_file = scope_file
        self.authorized_domains = []
        self.authorized_ips = []
        self.load_scope()

    def load_scope(self):
        try:
            with open(self.scope_file, 'r') as f:
                data = json.load(f)
                self.authorized_domains = data.get("authorized_domains", [])
                self.authorized_ips = data.get("authorized_ips", [])
        except Exception as e:
            logger.error(f"Failed to load scope file: {e}")

    def is_in_scope(self, target: str) -> bool:
        """
        Final check before any module execution.
        """
        if target in self.authorized_domains or target in self.authorized_ips:
            return True
            
        # Wildcard check
        for domain in self.authorized_domains:
            if domain.startswith("*."):
                if target.endswith(domain[1:]):
                    return True
        
        logger.warning(f"BLOCKED: Target '{target}' is NOT in authorized scope.")
        return False
