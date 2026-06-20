"""DARKWIN DNS Bruteforcer module.

Bruteforces subdomains using a wordlist and DNS resolution.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from pathlib import Path
from typing import Any, Dict, List

import dns.exception
import dns.resolver

MODULE_META: Dict[str, str] = {
    "name": "DNS Bruteforcer",
    "category": "Reconnaissance",
    "description": "Bruteforces subdomains using a wordlist",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Bruteforce subdomains using wordlists/subdomains.txt.

    Args:
        target: Domain to brute-force.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of resolved subdomain dicts, or empty if wordlist is missing.
    """
    subdomains: List[Dict[str, Any]] = []
    wordlist_path = Path("wordlists") / "subdomains.txt"

    if not wordlist_path.exists():
        return []

    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 2

    try:
        with wordlist_path.open("r", encoding="utf-8") as f:
            for line in f:
                sub = line.strip()
                if not sub:
                    continue
                full_domain = f"{sub}.{target}"
                try:
                    answers = resolver.resolve(full_domain, "A")
                    ips = [str(rdata) for rdata in answers]
                    subdomains.append({
                        "subdomain": full_domain,
                        "ips": ips,
                        "source": "bruteforce",
                        "scan_id": scan_id,
                    })
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, dns.exception.DNSException):
                    continue
    except (OSError, FileNotFoundError):
        pass

    return subdomains
