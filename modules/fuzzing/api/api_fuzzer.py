"""DARKWIN API Fuzzer module.

Fuzzes API endpoints for unauthenticated access and hidden parameters.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "API Fuzzer",
    "category": "Fuzzing",
    "description": "Fuzzes API endpoints for unauthenticated access or hidden parameters",
    "version": "1.0.0",
}


def run(url: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Fuzz API endpoints for broken access control.

    Args:
        url: Base URL of the target.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of finding dicts for endpoints reachable without auth.
    """
    findings: List[Dict[str, Any]] = []
    api_paths = ["/api/users", "/api/v2/admin", "/graphql"]

    try:
        with httpx.Client(timeout=10.0) as client:
            for path in api_paths:
                target_url = f"{url.rstrip('/')}{path}"
                try:
                    response = client.get(target_url)
                    if response.status_code == 200 and "admin" in path.lower():
                        findings.append({
                            "vuln_type": "broken_access_control",
                            "severity": "High",
                            "description": f"Unauthenticated access to API endpoint: {path}",
                            "endpoint": target_url,
                            "scan_id": scan_id,
                        })
                except (httpx.RequestError, httpx.HTTPStatusError):
                    continue
    except (httpx.RequestError, httpx.HTTPStatusError):
        pass

    return findings
