import whois
from typing import List, Dict

MODULE_META = {
    "name": "WHOIS Lookup",
    "category": "Reconnaissance",
    "description": "Retrieves WHOIS registration data for the target",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Performs a WHOIS lookup using python-whois.
    """
    try:
        w = whois.whois(target)
        # Convert to a serializable dict
        return [{
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers,
            "emails": w.emails,
            "org": w.org,
            "scan_id": scan_id
        }]
    except Exception:
        return []
