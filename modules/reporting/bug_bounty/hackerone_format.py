"""DARKWIN HackerOne Formatter module.

Formats vulnerability findings for HackerOne report submission.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Dict

MODULE_META: Dict[str, str] = {
    "name": "HackerOne Formatter",
    "category": "Reporting",
    "description": "Formats vulnerabilities for HackerOne reports",
    "version": "1.0.0",
}


def run(finding: dict, scan_id: str, config: dict) -> str:
    """Format a finding for HackerOne submission.

    Args:
        finding: Dict with ``description``, ``endpoint``, ``payload``.
        scan_id: Unique scan identifier (unused, kept for API consistency).
        config: Application config (unused, kept for API consistency).

    Returns:
        Formatted HackerOne report text.
    """
    return (
        f"\n**Summary:**"
        f"\n{finding.get('description')}"
        f"\n\n**Steps to Reproduce:**"
        f"\n1. Navigate to {finding.get('endpoint')}"
        f"\n2. Use payload: `{finding.get('payload')}`"
        f"\n\n**Impact:**"
        f"\nPotential account takeover or sensitive data exposure."
        "\n"
    )
