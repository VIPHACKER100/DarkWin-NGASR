import httpx
import json
from typing import List, Dict

MODULE_META = {
    "name": "GraphQL Fuzzer",
    "category": "Fuzzing",
    "description": "Fuzzes GraphQL endpoints for introspection and common queries",
    "version": "1.0.0"
}

def run(url: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Tests GraphQL endpoint for introspection and common queries.
    """
    findings = []
    introspection_query = {"query": "{__schema{types{name}}}"}
    
    try:
        with httpx.Client(timeout=10.0) as client:
            # Test Introspection
            response = client.post(url, json=introspection_query)
            if response.status_code == 200 and "data" in response.json():
                findings.append({
                    "vuln_type": "info_disclosure",
                    "severity": "Low",
                    "endpoint": url,
                    "description": "GraphQL Introspection is enabled.",
                    "scan_id": scan_id
                })
                
            # Fuzz common queries (simplified)
            common_queries = [
                {"query": "{users{username}}"},
                {"query": "{admin{id}}"},
                {"query": "{config{key}}"}
            ]
            for q in common_queries:
                resp = client.post(url, json=q)
                if resp.status_code == 200 and "errors" not in resp.text:
                    findings.append({
                        "type": "graphql_query",
                        "endpoint": url,
                        "payload": json.dumps(q),
                        "description": "Successful GraphQL query execution.",
                        "scan_id": scan_id
                    })
    except Exception:
        pass
        
    return findings
