"""DARKWIN Directory Fuzzer (lightweight) module.

Fuzzes for hidden directories and files using a built-in common-path list.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "Directory Fuzzer",
    "category": "Fuzzing",
    "description": "Fuzzes for hidden directories and files using common wordlists",
    "version": "1.0.0",
}


def run(url: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Fuzz web directories using a built-in path list.

    Args:
        url: Target URL.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of discovered endpoint dicts.
    """
    findings: List[Dict[str, Any]] = []
    common_paths = ["/admin", "/backup", "/.git/config", "/api/v1"]

    try:
        with httpx.Client(timeout=10.0, follow_redirects=False) as client:
            for path in common_paths:
                target_url = f"{url.rstrip('/')}{path}"
                try:
                    response = client.get(target_url)
                    if response.status_code in (200, 301, 403):
                        findings.append({
                            "vuln_type": "exposed_directory",
                            "severity": "Low" if response.status_code in (403, 301) else "Medium",
                            "description": f"Discovered endpoint: {path} (Status: {response.status_code})",
                            "endpoint": target_url,
                            "scan_id": scan_id,
                        })
                except (httpx.RequestError, httpx.HTTPStatusError):
                    continue
    except (httpx.RequestError, httpx.HTTPStatusError):
        pass

    return findings
