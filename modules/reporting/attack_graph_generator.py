"""DARKWIN Attack Graph Generator module.

Generates a Mermaid-style attack graph linking subdomains, services, and vulnerabilities.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from pathlib import Path
from typing import Any, Dict

MODULE_META: Dict[str, str] = {
    "name": "Attack Graph Generator",
    "category": "Reporting",
    "description": "Generates a visual attack graph linking subdomains, services, and vulnerabilities",
    "version": "1.0.0",
}


def run(scan_results: dict, scan_id: str, config: dict) -> str:
    """Generate a Mermaid-style attack graph from scan results.

    Args:
        scan_results: Dict with ``target`` and ``findings`` keys.
        scan_id: Unique scan identifier used for the output directory.
        config: Application config; may contain ``config["scans"]["output_dir"]``.

    Returns:
        Path to the generated Markdown file containing the Mermaid graph.
    """
    output_dir = Path(config.get("scans", {}).get("output_dir", "reports")) / scan_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "attack_graph.md"

    graph_content = "graph TD\n"
    target = scan_results.get("target", "Target")
    graph_content += f"    Root({target}) --> Subdomains\n"

    for v in scan_results.get("findings", []):
        endpoint = v.get("endpoint", "endpoint")
        vuln = v.get("vuln_type", "vulnerability")
        graph_content += f"    Subdomains --> {endpoint}\n"
        graph_content += f"    {endpoint} --> {vuln}(({vuln}))\n"
        if v.get("severity") in ("Critical", "High"):
            graph_content += f"    style {vuln} fill:#f96,stroke:#333,stroke-width:4px\n"

    with output_file.open("w", encoding="utf-8") as f:
        f.write(f"```mermaid\n{graph_content}\n```")

    return str(output_file)
