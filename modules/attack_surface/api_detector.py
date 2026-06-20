"""DARKWIN API Detector module.

Identifies potential API endpoints and specification files (Swagger, OpenAPI, GraphQL)
on a target web application.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "API Detector",
    "category": "Attack Surface",
    "description": "Identifies potential API endpoints and specifications",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Crawl the target for common API endpoint patterns.

    Args:
        target: Hostname or URL to scan.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of discovered API endpoint dicts.
    """
    api_endpoints: List[Dict[str, Any]] = []
    common_paths = [
        "/api/", "/v1/", "/v2/", "/graphql",
        "/swagger.json", "/openapi.json", "/api-docs",
        "/swagger-ui.html", "/docs",
    ]

    base_url = f"https://{target}" if not target.startswith("http") else target

    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            for path in common_paths:
                url = base_url.rstrip("/") + path
                try:
                    response = client.get(url)
                    if response.status_code in (200, 401, 403):
                        api_endpoints.append({
                            "url": url,
                            "status_code": response.status_code,
                            "scan_id": scan_id,
                        })
                except (httpx.RequestError, httpx.HTTPStatusError):
                    continue
    except (httpx.RequestError, httpx.HTTPStatusError):
        pass

    return api_endpoints
