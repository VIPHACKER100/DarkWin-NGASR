import httpx
from typing import List, Dict

MODULE_META = {
    "name": "ASN Lookup",
    "category": "Reconnaissance",
    "description": "Resolves ASN and network prefix for an IP using BGPView",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Queries BGPView API for ASN info. Target must be an IP.
    """
    url = f"https://api.bgpview.io/ip/{target}"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json().get("data", {})
                prefixes = data.get("prefixes", [])
                asn_data = []
                for p in prefixes:
                    asn_data.append({
                        "ip": target,
                        "asn": p.get("asn", {}).get("asn"),
                        "name": p.get("asn", {}).get("name"),
                        "description": p.get("asn", {}).get("description"),
                        "prefix": p.get("prefix"),
                        "scan_id": scan_id
                    })
                return asn_data
    except Exception:
        pass
    
    return []
