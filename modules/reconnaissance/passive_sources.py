import httpx
import re
import asyncio
from typing import List, Dict, Set
from core.logging_system import get_logger

logger = get_logger("PassiveSources")

MODULE_META = {
    "name": "Passive Sources Aggregator",
    "category": "Reconnaissance",
    "description": "Aggregates subdomains from multiple passive sources (RapidDNS, Archive, etc.)",
    "version": "1.1.0"
}

async def fetch_archive_org(domain: str) -> Set[str]:
    """Fetch subdomains from web.archive.org"""
    subdomains = set()
    url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=text&fl=original&collapse=urlkey"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                # Extract domains from URLs
                for line in resp.text.splitlines():
                    match = re.search(r'https?://([^/]+)', line)
                    if match:
                        sub = match.group(1).lower()
                        if sub.endswith(f".{domain}"):
                            subdomains.add(sub)
    except Exception as e:
        logger.warning(f"Archive.org error: {e}")
    return subdomains

async def fetch_crt_sh(domain: str) -> Set[str]:
    """Fetch subdomains from crt.sh"""
    subdomains = set()
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                for entry in data:
                    names = entry.get("name_value", "").split("\n")
                    for name in names:
                        name = name.replace("*.", "").lower()
                        if name.endswith(f".{domain}"):
                            subdomains.add(name)
    except Exception as e:
        logger.warning(f"crt.sh error: {e}")
    return subdomains

async def fetch_rapiddns(domain: str) -> Set[str]:
    """Fetch subdomains from rapiddns.io"""
    subdomains = set()
    url = f"https://rapiddns.io/subdomain/{domain}?full=1#result"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                matches = re.findall(rf'<td>([a-zA-Z0-9._-]+\.{re.escape(domain)})</td>', resp.text)
                for m in matches:
                    subdomains.add(m.lower())
    except Exception as e:
        logger.warning(f"RapidDNS error: {e}")
    return subdomains

async def fetch_jldc(domain: str) -> Set[str]:
    """Fetch subdomains from jldc.me"""
    subdomains = set()
    url = f"https://jldc.me/anubis/subdomains/{domain}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                # Simple regex for domains
                matches = re.findall(rf'([a-zA-Z0-9._-]+\.{re.escape(domain)})', resp.text)
                for m in matches:
                    subdomains.add(m.lower())
    except Exception as e:
        logger.warning(f"JLDC error: {e}")
    return subdomains

async def run(domain: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Main entry point for the passive sources module.
    """
    logger.info(f"Starting passive subdomain discovery for {domain}")
    
    tasks = [
        fetch_archive_org(domain),
        fetch_crt_sh(domain),
        fetch_rapiddns(domain),
        fetch_jldc(domain)
    ]
    
    results = await asyncio.gather(*tasks)
    
    all_subs = set()
    for res in results:
        all_subs.update(res)
        
    logger.info(f"Discovered {len(all_subs)} unique subdomains from passive sources")
    
    findings = []
    for sub in all_subs:
        findings.append({
            "vuln_type": "subdomain",
            "severity": "Info",
            "endpoint": sub,
            "description": f"Discovered passive subdomain: {sub}",
            "scan_id": scan_id
        })
        
    return findings
