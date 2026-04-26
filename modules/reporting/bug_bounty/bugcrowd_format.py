from typing import List, Dict

MODULE_META = {
    "name": "Bugcrowd Formatter",
    "category": "Reporting",
    "description": "Formats vulnerabilities for Bugcrowd VRT alignment",
    "version": "1.0.0"
}

def run(finding: dict, scan_id: str, config: dict) -> str:
    """
    Formats a finding for Bugcrowd.
    """
    return f"""
**Vulnerability Type:** {finding.get('vuln_type')}
**VRT Category:** Server-side Injection -> {finding.get('vuln_type').upper()}

**Description:**
{finding.get('description')}

**URL:**
{finding.get('endpoint')}
"""
