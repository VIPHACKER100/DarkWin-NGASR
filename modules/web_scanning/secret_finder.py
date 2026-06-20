"""DARKWIN Secret & API Key Finder module.

Scans HTTP response bodies for leaked secrets, API keys, and sensitive tokens
using regex patterns inspired by bug-bounty one-liners.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import re
from typing import Dict, List

import httpx

from core.logging_system import get_logger

logger = get_logger("SecretFinder")

MODULE_META: Dict[str, str] = {
    "name": "Secret & API Key Finder",
    "category": "Web Scanning",
    "description": "Scans page content for leaked secrets, API keys, and sensitive tokens.",
    "version": "1.0.0",
}

SECRET_PATTERNS: Dict[str, str] = {
    "AWS Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret": r"[\"|']?secret_key[\"|']?[:|=]\s*[\"|']?([a-zA-Z0-9+/]{40})[\"|']?",
    "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
    "Firebase URL": r"https://[a-z0-9.-]+\.firebaseio\.com",
    "Slack Webhook": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+",
    "GitHub Token": r"ghp_[a-zA-Z0-9]{36}",
    "JWT Token": r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
    "Stripe Key": r"sk_live_[0-9a-zA-Z]{24}",
    "Private Key": r"-----BEGIN [A-Z ]+ PRIVATE KEY-----",
    "Generic Secret": r"(?i)(secret|token|password|auth|api_key|config)\s*[:|=]\s*[\"|']?([a-zA-Z0-9\-_]{16,})[\"|']?",
}


async def scan_content(url: str, content: str, scan_id: str) -> List[Dict]:
    """Scan response content for secret patterns.

    Args:
        url: The URL that was scanned (included in each finding).
        content: The HTTP response body text.
        scan_id: Unique scan identifier.

    Returns:
        A list of finding dicts, one per matched secret.
    """
    findings: List[Dict] = []
    for name, pattern in SECRET_PATTERNS.items():
        for match in re.finditer(pattern, content):
            secret = match.group(0)
            if name == "Generic Secret" and len(secret) < 20:
                continue
            findings.append({
                "vuln_type": "leaked_secret",
                "severity": "High" if name != "Generic Secret" else "Medium",
                "description": f"Found potential {name} in response body.",
                "endpoint": url,
                "payload": secret[:50] + "..." if len(secret) > 50 else secret,
                "scan_id": scan_id,
            })
    return findings


async def run(url: str, scan_id: str, config: dict) -> List[Dict]:
    """Scan a single URL for secrets.

    Args:
        url: Target URL to fetch and inspect.
        scan_id: Unique scan identifier.
        config: Module configuration (unused, kept for API consistency).

    Returns:
        List of finding dicts, or an empty list on failure.
    """
    findings: List[Dict] = []
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, verify=False) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                findings = await scan_content(url, resp.text, scan_id)
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.debug(f"Secret scan failed for {url}: {e}")

    return findings
