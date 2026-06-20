"""DARKWIN Markdown Reporter module.

Generates a clean Markdown report suitable for GitHub, Obsidian, or plain-text sharing.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from pathlib import Path
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "Markdown Reporter",
    "category": "Reporting",
    "description": "Generates a clean Markdown report suitable for GitHub or Obsidian",
    "version": "1.0.0",
}


def run(scan_results: dict, scan_id: str, config: dict) -> str:
    """Generate a Markdown report from scan results.

    Args:
        scan_results: Dict with ``target``, ``date``, and ``findings`` keys.
        scan_id: Unique scan identifier used for the output directory.
        config: Application config; may contain ``config["scans"]["output_dir"]``.

    Returns:
        Path to the generated Markdown file.
    """
    output_dir = Path(config.get("scans", {}).get("output_dir", "reports")) / scan_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "report.md"

    findings: List[Dict[str, Any]] = scan_results.get("findings", [])
    critical_count = sum(1 for v in findings if v.get("severity") == "Critical")
    high_count = sum(1 for v in findings if v.get("severity") == "High")

    md_content = (f"# DARKWIN Scan Report\n"
                  f"## Developed by ARYAN AHIRWAR (VIPHACKER.100)\n\n"
                  f"**Scan ID:** {scan_id}\n"
                  f"**Target:** {scan_results.get('target')}\n"
                  f"**Date:** {scan_results.get('date')}\n\n"
                  f"---\n\n"
                  f"### Summary\n"
                  f"- Total Findings: {len(findings)}\n"
                  f"- Critical: {critical_count}\n"
                  f"- High: {high_count}\n\n"
                  f"### Findings\n")

    for v in findings:
        md_content += (f"\n#### [{v.get('severity')}] {v.get('vuln_type', '').upper()}\n"
                       f"- **Endpoint:** `{v.get('endpoint')}`\n"
                       f"- **Description:** {v.get('description')}\n"
                       f"- **Payload:** `{v.get('payload')}`\n")

    output_file.write_text(md_content, encoding="utf-8")
    return str(output_file)
