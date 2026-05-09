import httpx
import re
from typing import List, Dict

MODULE_META = {
    "name": "JavaScript Analyzer",
    "category": "Web Scanning",
    "description": "Scans JS files for secrets, API endpoints, and internal links",
    "version": "1.0.0"
}

def run(js_url: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Analyzes a JS file for sensitive information.
    """
    findings = []
    
    patterns = {
        "api_endpoint": r'["\']((?:https?://|//)?/[a-zA-Z0-9_/?=&%.-]*)["\']',
        "aws_key": r'AKIA[0-9A-Z]{16}',
        "jwt_token": r'eyJh[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
        "generic_secret": r'(?i)(api_key|secret|password|auth|token|access_key|private_key)["\']\s*[:=]\s*["\']([a-zA-Z0-9-_]{8,})["\']',
        "firebase_url": r'https://[a-zA-Z0-9-]+\.firebaseio\.com',
        "s3_bucket": r'[a-zA-Z0-9-.]+\.s3\.amazonaws\.com'
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(js_url)
            if response.status_code == 200:
                content = response.text
                
                for p_name, p_regex in patterns.items():
                    matches = re.finditer(p_regex, content)
                    for match in matches:
                        findings.append({
                            "type": p_name,
                            "value": match.group(0),
                            "url": js_url,
                            "scan_id": scan_id
                        })
    except Exception:
        pass
        
    return findings
