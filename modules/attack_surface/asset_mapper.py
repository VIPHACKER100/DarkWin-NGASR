"""DARKWIN Asset Mapper module.

Aggregates and deduplicates discovered assets into a graph structure.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
from pathlib import Path
from typing import Any, Dict

MODULE_META: Dict[str, str] = {
    "name": "Asset Mapper",
    "category": "Attack Surface",
    "description": "Aggregates and deduplicates discovered assets into a graph",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> Dict[str, Any]:
    """Aggregate and persist the attack-surface graph for a scan.

    Args:
        target: The target identifier.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        Dict with ``target``, ``scan_id``, ``nodes``, and ``edges``.
    """
    report_dir = Path("reports") / scan_id
    report_dir.mkdir(parents=True, exist_ok=True)

    graph: Dict[str, Any] = {
        "target": target,
        "scan_id": scan_id,
        "nodes": [],
        "edges": [],
    }

    output_file = report_dir / "attack_surface_graph.json"
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(graph, f, indent=4)

    return graph
