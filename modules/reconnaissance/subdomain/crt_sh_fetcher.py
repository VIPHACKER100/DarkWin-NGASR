import httpx
from typing import List, Dict

MODULE_META = {
    "name": "crt.sh Fetcher",
    "category": "Reconnaissance",
    "description": "Queries crt.sh for subdomain certificates",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Queries crt.sh API for certificates related to the target domain.
    """
    subdomains = []
    url = f"https://crt.sh/?q=%.{target}&output=json"
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json()
                seen = set()
                for entry in data:
                    name_value = entry.get("name_value", "")
                    # crt.sh can return multiple names separated by \n
                    for name in name_value.split("\n"):
                        name = name.strip().lower()
                        if name.endswith(target) and name not in seen:
                            if "*" not in name: # Exclude wildcards for simple list
                                subdomains.append({
                                    "subdomain": name,
                                    "source": "crt.sh",
                                    "scan_id": scan_id
                                })
                                seen.add(name)
    except Exception as e:
        pass
    
    return subdomains
