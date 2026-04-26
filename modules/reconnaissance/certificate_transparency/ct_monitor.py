import httpx
from typing import List, Dict

MODULE_META = {
    "name": "CT Monitor",
    "category": "Reconnaissance",
    "description": "Polls crt.sh for new certificates issued recently",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Polls crt.sh for new certificates for the target domain.
    """
    # In a full implementation, this would compare against previously seen certs in DB
    # For now, it fetches the latest list from crt.sh
    from modules.reconnaissance.subdomain.crt_sh_fetcher import run as fetch_crt
    results = fetch_crt(target, scan_id, config)
    return results
