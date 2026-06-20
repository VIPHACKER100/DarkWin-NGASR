"""DARKWIN JavaScript Analyzer module.

Scans JavaScript files for secrets, API endpoints, and other sensitive data.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import re
from typing import Any, Dict, List

import httpx

MODULE_META: Dict[str, str] = {
    "name": "JavaScript Analyzer",
    "category": "Web Scanning",
    "description": "Scans JS files for secrets, API endpoints, and internal links",
    "version": "1.0.0",
}

PATTERNS: Dict[str, str] = {
    "api_endpoint": r'["\']((?:https?://|//)?/[a-zA-Z0-9_/?=&%.-]*)["\']',
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "jwt_token": r"eyJh[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    "generic_secret": (
        r'(?i)(api_key|secret|password|auth|token|access_key|private_key)'
        r'["\']\s*[:=]\s*["\']([a-zA-Z0-9-_]{8,})["\']'
    ),
    "firebase_url": r"https://[a-zA-Z0-9-]+\.firebaseio\.com",
    "s3_bucket": r"[a-zA-Z0-9-.]+\.s3\.amazonaws\.com",
}


def run(js_url: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Analyze a JavaScript file for sensitive information.

    Args:
        js_url: URL of the JavaScript file to fetch and scan.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of finding dicts with ``type``, ``value``, ``url``, ``scan_id``.
    """
    findings: List[Dict[str, Any]] = []

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(js_url)
            if response.status_code == 200:
                content = response.text
                for p_name, p_regex in PATTERNS.items():
                    for match in re.finditer(p_regex, content):
                        findings.append({
                            "type": p_name,
                            "value": match.group(0),
                            "url": js_url,
                            "scan_id": scan_id,
                        })
    except (httpx.RequestError, httpx.HTTPStatusError):
        pass

    return findings
