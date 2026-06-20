"""DARKWIN Reverse IP Lookup module.

Queries HackerTarget for domains hosted on the same IP address.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "Reverse IP Lookup",
    "category": "Reconnaissance",
    "description": "Queries HackerTarget for domains hosted on the same IP",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Query HackerTarget Reverse IP Lookup API.

    Args:
        target: IP address or domain to reverse-lookup.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of domain dicts, or empty on failure / no results.
    """
    domains: List[Dict[str, Any]] = []
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
                                "scan_id": scan_id,
                            })
    except (httpx.RequestError, httpx.HTTPStatusError):
        pass

    return domains
