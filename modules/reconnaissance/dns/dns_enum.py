"""DARKWIN DNS Enumerator module.

Performs standard DNS record lookups (A, AAAA, MX, NS, TXT, CNAME, SOA).

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Any, Dict, List

import dns.resolver
import dns.exception

MODULE_META: Dict[str, str] = {
    "name": "DNS Enumerator",
    "category": "Reconnaissance",
    "description": "Performs standard DNS record lookups (A, AAAA, MX, NS, TXT, CNAME, SOA)",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Perform DNS lookups for common record types.

    Args:
        target: Domain to query.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of DNS record dicts.
    """
    records: List[Dict[str, Any]] = []
    record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]

    resolver = dns.resolver.Resolver()
    resolver.timeout = 5
    resolver.lifetime = 5

    for r_type in record_types:
        try:
            answers = resolver.resolve(target, r_type)
            for rdata in answers:
                records.append({
                    "type": r_type,
                    "value": str(rdata),
                    "scan_id": scan_id,
                })
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, dns.exception.DNSException):
            continue

    return records
