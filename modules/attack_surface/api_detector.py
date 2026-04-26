import httpx
from bs4 import BeautifulSoup
from typing import List, Dict

MODULE_META = {
    "name": "API Detector",
    "category": "Attack Surface",
    "description": "Identifies potential API endpoints and specifications",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Crawls the target for common API patterns.
    """
    api_endpoints = []
    common_paths = [
        "/api/", "/v1/", "/v2/", "/graphql", 
        "/swagger.json", "/openapi.json", "/api-docs",
        "/swagger-ui.html", "/docs"
    ]
    
    base_url = f"https://{target}" if not target.startswith("http") else target
    
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            for path in common_paths:
                url = base_url.rstrip('/') + path
                try:
                    response = client.get(url)
                    if response.status_code in [200, 401, 403]:
                        api_endpoints.append({
                            "url": url,
                            "status_code": response.status_code,
                            "scan_id": scan_id
                        })
                except Exception:
                    continue
    except Exception:
        pass
        
    return api_endpoints
