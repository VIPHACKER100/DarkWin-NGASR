import httpx
import re
import asyncio
from typing import List, Dict, Set
from core.logging_system import get_logger

logger = get_logger("SecretFinder")

MODULE_META = {
    "name": "Secret & API Key Finder",
    "category": "Web Scanning",
    "description": "Scans page content for leaked secrets, API keys, and sensitive tokens.",
    "version": "1.0.0"
}

# Regex patterns inspired by bug bounty one-liners
SECRET_PATTERNS = {
    "AWS Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret": r"[\"|']?secret_key[\"|']?[:|=]\s*[\"|']?([a-zA-Z0-9+/]{40})[\"|']?",
    "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
    "Firebase URL": r"https://[a-z0-9.-]+\.firebaseio\.com",
    "Slack Webhook": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+",
    "GitHub Token": r"ghp_[a-zA-Z0-9]{36}",
    "JWT Token": r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
    "Stripe Key": r"sk_live_[0-9a-zA-Z]{24}",
    "Private Key": r"-----BEGIN [A-Z ]+ PRIVATE KEY-----",
    "Generic Secret": r"(?i)(secret|token|password|auth|api_key|config)\s*[:|=]\s*[\"|']?([a-zA-Z0-9\-_]{16,})[\"|']?"
}

async def scan_content(url: str, content: str, scan_id: str) -> List[Dict]:
    findings = []
    for name, pattern in SECRET_PATTERNS.items():
        matches = re.finditer(pattern, content)
        for match in matches:
            secret = match.group(0)
            # Basic entropy or length check to reduce false positives for "Generic Secret"
            if name == "Generic Secret" and len(secret) < 20:
                continue
                
            findings.append({
                "vuln_type": "leaked_secret",
                "severity": "High" if name != "Generic Secret" else "Medium",
                "description": f"Found potential {name} in response body.",
                "endpoint": url,
                "payload": secret[:50] + "..." if len(secret) > 50 else secret,
                "scan_id": scan_id
            })
    return findings

async def run(url: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Scans a single URL for secrets.
    """
    findings = []
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, verify=False) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                findings = await scan_content(url, resp.text, scan_id)
    except Exception as e:
        logger.debug(f"Secret scan failed for {url}: {e}")
        
    return findings
