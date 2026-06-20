"""DARKWIN crt.sh Fetcher module.

Queries crt.sh for certificate transparency subdomain entries.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Any, Dict, List

import httpx

MODULE_META: Dict[str, str] = {
    "name": "crt.sh Fetcher",
    "category": "Reconnaissance",
    "description": "Queries crt.sh for subdomain certificates",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Query crt.sh API for certificates related to a target domain.

    Args:
        target: Domain to query (e.g. ``example.com``).
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of subdomain dicts (wildcards excluded).
    """
    subdomains: List[Dict[str, Any]] = []
    url = f"https://crt.sh/?q=%.{target}&output=json"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                data: Any = response.json()
                seen: set = set()
                for entry in data if isinstance(data, list) else []:
                    name_value = entry.get("name_value", "")
                    for name in name_value.split("\n"):
                        name = name.strip().lower()
                        if name.endswith(target) and name not in seen and "*" not in name:
                            subdomains.append({
                                "subdomain": name,
                                "source": "crt.sh",
                                "scan_id": scan_id,
                            })
                            seen.add(name)
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
        pass

    return subdomains
