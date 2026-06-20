"""DARKWIN GraphQL Fuzzer module.

Fuzzes GraphQL endpoints for introspection and common query execution.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
from typing import Any, Dict, List

import httpx

MODULE_META: Dict[str, str] = {
    "name": "GraphQL Fuzzer",
    "category": "Fuzzing",
    "description": "Fuzzes GraphQL endpoints for introspection and common queries",
    "version": "1.0.0",
}


def run(url: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Test a GraphQL endpoint for introspection and common query access.

    Args:
        url: GraphQL endpoint URL.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of finding dicts.
    """
    findings: List[Dict[str, Any]] = []
    introspection_query: Dict[str, str] = {"query": "{__schema{types{name}}}"}

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=introspection_query)
            if response.status_code == 200 and "data" in response.json():
                findings.append({
                    "vuln_type": "info_disclosure",
                    "severity": "Low",
                    "endpoint": url,
                    "description": "GraphQL Introspection is enabled.",
                    "scan_id": scan_id,
                })

            common_queries = [
                {"query": "{users{username}}"},
                {"query": "{admin{id}}"},
                {"query": "{config{key}}"},
            ]
            for q in common_queries:
                try:
                    resp = client.post(url, json=q)
                    if resp.status_code == 200 and "errors" not in resp.text:
                        findings.append({
                            "type": "graphql_query",
                            "endpoint": url,
                            "payload": json.dumps(q),
                            "description": "Successful GraphQL query execution.",
                            "scan_id": scan_id,
                        })
                except (httpx.RequestError, httpx.HTTPStatusError):
                    continue
    except (httpx.RequestError, httpx.HTTPStatusError):
        pass

    return findings
