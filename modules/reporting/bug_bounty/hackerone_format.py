from typing import List, Dict

MODULE_META = {
    "name": "HackerOne Formatter",
    "category": "Reporting",
    "description": "Formats vulnerabilities for HackerOne reports",
    "version": "1.0.0"
}

def run(finding: dict, scan_id: str, config: dict) -> str:
    """
    Formats a finding for HackerOne.
    """
    return f"""
**Summary:**
{finding.get('description')}

**Steps to Reproduce:**
1. Navigate to {finding.get('endpoint')}
2. Use payload: `{finding.get('payload')}`

**Impact:**
Potential account takeover or sensitive data exposure.
"""
