import httpx
from typing import List, Dict

def run_censys_search(query: str, config: dict) -> List[Dict]:
    """
    Searches Censys for the given query.
    """
    api_id = config.get("api_keys", {}).get("censys_id", "")
    api_secret = config.get("api_keys", {}).get("censys_secret", "")
    
    if not api_id or not api_secret:
        return []
        
    url = "https://search.censys.io/api/v2/hosts/search"
    params = {"q": query}
    
    try:
        with httpx.Client(auth=(api_id, api_secret), timeout=10.0) as client:
            response = client.get(url, params=params)
            if response.status_code == 200:
                return response.json().get("result", {}).get("hits", [])
    except Exception:
        pass
        
    return []
