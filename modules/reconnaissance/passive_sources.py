"""DARKWIN Passive Sources Aggregator module.

Aggregates subdomains from multiple passive sources (Archive.org, crt.sh,
RapidDNS, JLDC) using async HTTP clients.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import asyncio
import re
from typing import Dict, List, Set

import httpx

from core.logging_system import get_logger

logger = get_logger("PassiveSources")

MODULE_META: Dict[str, str] = {
    "name": "Passive Sources Aggregator",
    "category": "Reconnaissance",
    "description": "Aggregates subdomains from multiple passive sources (RapidDNS, Archive, etc.)",
    "version": "1.1.0",
}


async def _fetch_source(domain: str, url: str, extract: str = "json") -> Set[str]:
    """Fetch subdomains from a passive source and extract domain-like strings."""
    subs: Set[str] = set()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return subs
            if extract == "json":
                data = resp.json()
                for entry in data if isinstance(data, list) else data:
                    names = entry.get("name_value", "") if isinstance(entry, dict) else ""
                    for name in names.split("\n"):
                        name = name.replace("*.", "").lower()
                        if name.endswith(f".{domain}"):
                            subs.add(name)
                return subs
            # HTML/text extraction
            pattern = rf'([a-zA-Z0-9._-]+\.{re.escape(domain)})'
            for m in re.finditer(pattern, resp.text):
                subs.add(m.group(1).lower())
            return subs
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as e:
        logger.warning(f"Passive source fetch failed for {url}: {e}")
        return subs


async def fetch_archive_org(domain: str) -> Set[str]:
    """Fetch subdomains from web.archive.org."""
    url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=text&fl=original&collapse=urlkey"
    subs: Set[str] = set()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                for line in resp.text.splitlines():
                    m = re.search(r'https?://([^/]+)', line)
                    if m:
                        sub = m.group(1).lower()
                        if sub.endswith(f".{domain}"):
                            subs.add(sub)
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.warning(f"Archive.org error: {e}")
    return subs


async def fetch_crt_sh(domain: str) -> Set[str]:
    """Fetch subdomains from crt.sh."""
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    return await _fetch_source(domain, url, extract="json")


async def fetch_rapiddns(domain: str) -> Set[str]:
    """Fetch subdomains from rapiddns.io."""
    url = f"https://rapiddns.io/subdomain/{domain}?full=1#result"
    return await _fetch_source(domain, url, extract="html")


async def fetch_jldc(domain: str) -> Set[str]:
    """Fetch subdomains from jldc.me (Anubis)."""
    url = f"https://jldc.me/anubis/subdomains/{domain}"
    return await _fetch_source(domain, url, extract="json")


async def run(domain: str, scan_id: str, config: dict) -> List[Dict]:
    """Aggregate subdomains from all passive sources.

    Args:
        domain: Target domain (e.g. ``example.com``).
        scan_id: Unique scan identifier.
        config: Application config (unused).

    Returns:
        List of subdomain finding dicts.
    """
    logger.info(f"Starting passive subdomain discovery for {domain}")

    results = await asyncio.gather(
        fetch_archive_org(domain),
        fetch_crt_sh(domain),
        fetch_rapiddns(domain),
        fetch_jldc(domain),
    )

    all_subs: Set[str] = set()
    for res in results:
        all_subs.update(res)

    logger.info(f"Discovered {len(all_subs)} unique subdomains from passive sources")

    findings: List[Dict] = []
    for sub in sorted(all_subs):
        findings.append({
            "vuln_type": "subdomain",
            "severity": "Info",
            "endpoint": sub,
            "description": f"Discovered passive subdomain: {sub}",
            "scan_id": scan_id,
        })

    return findings
