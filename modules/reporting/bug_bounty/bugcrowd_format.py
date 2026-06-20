"""DARKWIN Bugcrowd Formatter module.

Formats vulnerability findings for Bugcrowd VRT-aligned submission.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Dict

MODULE_META: Dict[str, str] = {
    "name": "Bugcrowd Formatter",
    "category": "Reporting",
    "description": "Formats vulnerabilities for Bugcrowd VRT alignment",
    "version": "1.0.0",
}


def run(finding: dict, scan_id: str, config: dict) -> str:
    """Format a finding for Bugcrowd submission.

    Args:
        finding: Dict with ``vuln_type``, ``description``, ``endpoint``.
        scan_id: Unique scan identifier (included in output).
        config: Application config (unused, kept for API consistency).

    Returns:
        Formatted Bugcrowd report text.
    """
    return (
        f"\n**Vulnerability Type:** {finding.get('vuln_type')}"
        f"\n**VRT Category:** Server-side Injection -> {finding.get('vuln_type', '').upper()}"
        f"\n\n**Description:**"
        f"\n{finding.get('description')}"
        f"\n\n**URL:**"
        f"\n{finding.get('endpoint')}"
        "\n"
    )
