import httpx
from typing import List, Dict

MODULE_META = {
    "name": "Reverse IP Lookup",
    "category": "Reconnaissance",
    "description": "Queries HackerTarget for domains hosted on the same IP",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Queries HackerTarget Reverse IP Lookup API.
    Target should be an IP address or a domain (which HackerTarget resolves).
    """
    domains = []
    url = f"https://api.hackertarget.com/reverseiplookup/?q={target}"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                text = response.text.strip()
                if "error" not in text.lower():
                    for line in text.splitlines():
                        if line.strip():
                            domains.append({
                                "domain": line.strip(),
                                "source": "hackertarget",
                                "scan_id": scan_id
                            })
    except Exception:
        pass
    
    return domains
