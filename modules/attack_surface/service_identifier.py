"""DARKWIN Service Identifier module.

Identifies services and versions on live hosts using nmap.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "Service Identifier",
    "category": "Attack Surface",
    "description": "Identifies services and versions on live hosts using nmap",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Run nmap for service detection on a target IP.

    Args:
        target: Hostname or IP to scan.
        scan_id: Unique scan identifier.
        config: Application config; expects ``config["tools"]["nmap"]``.

    Returns:
        List of result dicts, or empty on failure.
    """
    results: List[Dict[str, Any]] = []
    tmp = Path(tempfile.gettempdir()) / f"nmap_{scan_id}.xml"
    output_file = str(tmp)

    try:
        nmap_path = config.get("tools", {}).get("nmap", "nmap")
        cmd = [nmap_path, "-sV", "-Pn", "--top-ports", "100", "-oX", output_file, target]
        subprocess.run(cmd, capture_output=True, text=True, check=False)

        if tmp.exists():
            results.append({
                "host": target,
                "nmap_output_file": output_file,
                "status": "completed",
                "scan_id": scan_id,
            })
    except (subprocess.SubprocessError, OSError):
        pass

    return results
