import shodan
from typing import List, Dict

def run_shodan_search(query: str, config: dict) -> List[Dict]:
    """
    Searches Shodan for the given query.
    """
    api_key = config.get("api_keys", {}).get("shodan", "")
    if not api_key:
        return []
        
    api = shodan.Shodan(api_key)
    try:
        results = api.search(query)
        return results.get("matches", [])
    except Exception:
        return []

def get_host_info(ip: str, config: dict) -> Dict:
    """
    Retrieves detailed host information from Shodan.
    """
    api_key = config.get("api_keys", {}).get("shodan", "")
    if not api_key:
        return {}
        
    api = shodan.Shodan(api_key)
    try:
        return api.host(ip)
    except Exception:
        return {}
