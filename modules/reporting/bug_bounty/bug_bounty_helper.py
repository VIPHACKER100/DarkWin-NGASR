"""DARKWIN Bug Bounty Helper module.

Drafts professional bug-bounty report templates for HackerOne / Bugcrowd submissions.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Dict

MODULE_META: Dict[str, str] = {
    "name": "Bug Bounty Helper",
    "category": "Reporting",
    "description": "Assists in drafting professional bug bounty reports for HackerOne/Bugcrowd",
    "version": "1.0.0",
}


def run(finding: dict, scan_id: str, config: dict) -> str:
    """Draft a bug-bounty report template for a single finding.

    Args:
        finding: Dict with ``description``, ``endpoint``, ``payload``, ``vuln_type``.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        Formatted report template string.
    """
    return (
        f"\n## Summary:"
        f"\n{finding.get('description')}"
        f"\n\n## Steps To Reproduce:"
        f"\n1. Navigate to {finding.get('endpoint')}"
        f"\n2. Input payload: `{finding.get('payload')}`"
        f"\n3. Observe {finding.get('vuln_type')} vulnerability."
        f"\n\n## Supporting Material/References:"
        f"\n- DARKWIN Scan ID: {scan_id}"
        f"\n- Author: ARYAN AHIRWAR (VIPHACKER.100)"
        f"\n\n## Impact:"
        f"\nExplain the impact here based on the vulnerability type."
        "\n"
    )
