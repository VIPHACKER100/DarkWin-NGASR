"""DARKWIN ASN Lookup module.

Resolves ASN and network prefix information for an IP address using BGPView API.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "ASN Lookup",
    "category": "Reconnaissance",
    "description": "Resolves ASN and network prefix for an IP using BGPView",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Query BGPView API for ASN information.

    Args:
        target: IP address to look up.
        scan_id: Unique scan identifier.
        config: Application config (unused).

    Returns:
        List of prefix dicts with ASN details, or empty on failure.
    """
    url = f"https://api.bgpview.io/ip/{target}"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                data: Any = response.json().get("data", {})
                prefixes: Any = data.get("prefixes", [])
                return [
                    {
                        "ip": target,
                        "asn": p.get("asn", {}).get("asn"),
                        "name": p.get("asn", {}).get("name"),
                        "description": p.get("asn", {}).get("description"),
                        "prefix": p.get("prefix"),
                        "scan_id": scan_id,
                    }
                    for p in prefixes
                ]
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
        pass

    return []
