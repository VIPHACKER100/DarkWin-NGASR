"""DARKWIN WHOIS Lookup module.

Retrieves WHOIS registration data for a target domain using python-whois.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Any, Dict, List

import whois
import whois.parser

MODULE_META: Dict[str, str] = {
    "name": "WHOIS Lookup",
    "category": "Reconnaissance",
    "description": "Retrieves WHOIS registration data for the target",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Perform a WHOIS lookup for a target domain.

    Args:
        target: Domain to query.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List containing a single WHOIS data dict, or empty on failure.
    """
    try:
        w = whois.whois(target)
        return [{
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers,
            "emails": w.emails,
            "org": w.org,
            "scan_id": scan_id,
        }]
    except (whois.parser.PywhoisError, OSError, UnicodeDecodeError):
        return []
