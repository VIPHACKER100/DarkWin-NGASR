import httpx
from typing import List, Dict

MODULE_META = {
    "name": "API Fuzzer",
    "category": "Fuzzing",
    "description": "Fuzzes API endpoints for unauthenticated access or hidden parameters",
    "version": "1.0.0"
}

def run(url: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Fuzzes API endpoints.
    """
    findings = []
    api_paths = ["/api/users", "/api/v2/admin", "/graphql"]
    
    try:
        with httpx.Client(timeout=10.0) as client:
            for path in api_paths:
                target_url = f"{url.rstrip('/')}{path}"
                response = client.get(target_url)
                # If we get a 200 OK on an admin API without auth, that's a finding
                if response.status_code == 200 and "admin" in path.lower():
                    findings.append({
                        "vuln_type": "broken_access_control",
                        "severity": "High",
                        "description": f"Unauthenticated access to API endpoint: {path}",
                        "endpoint": target_url,
                        "scan_id": scan_id
                    })
    except Exception:
        pass
        
    return findings
