"""DARKWIN CT Monitor module.

Polls crt.sh for newly issued certificates for a target domain.
Delegates to the crt.sh subdomain fetcher.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "CT Monitor",
    "category": "Reconnaissance",
    "description": "Polls crt.sh for new certificates issued recently",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Poll crt.sh for new certificates.

    Args:
        target: Domain to monitor.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of certificate/subdomain findings from crt.sh.
    """
    from modules.reconnaissance.subdomain.crt_sh_fetcher import run as fetch_crt

    return fetch_crt(target, scan_id, config)
