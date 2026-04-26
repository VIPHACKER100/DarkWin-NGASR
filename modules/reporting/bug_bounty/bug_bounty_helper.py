from typing import List, Dict

MODULE_META = {
    "name": "Bug Bounty Helper",
    "category": "Reporting",
    "description": "Assists in drafting professional bug bounty reports for HackerOne/Bugcrowd",
    "version": "1.0.0"
}

def run(finding: dict, scan_id: str, config: dict) -> str:
    """
    Drafts a bug bounty report template for a single finding.
    """
    template = f"""
## Summary:
{finding.get('description')}

## Steps To Reproduce:
1. Navigate to {finding.get('endpoint')}
2. Input payload: `{finding.get('payload')}`
3. Observe {finding.get('vuln_type')} vulnerability.

## Supporting Material/References:
- DARKWIN Scan ID: {scan_id}
- Author: ARYAN AHIRWAR (VIPHACKER.100)

## Impact:
Explain the impact here based on the vulnerability type.
"""
    return template
