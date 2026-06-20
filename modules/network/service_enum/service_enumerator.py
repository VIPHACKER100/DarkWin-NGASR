"""DARKWIN Service Enumerator module.

Uses nmap for detailed service and version enumeration on specified ports.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "Service Enumerator",
    "category": "Network",
    "description": "Uses nmap for detailed service and version enumeration",
    "version": "1.0.0",
}


def run(target: str, ports: List[int], scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Run nmap for service detection on specific ports.

    Args:
        target: Hostname or IP to scan.
        ports: List of port numbers to probe.
        scan_id: Unique scan identifier.
        config: Application config; expects ``config["tools"]["nmap"]``.

    Returns:
        List of result dicts, or empty on failure.
    """
    results: List[Dict[str, Any]] = []
    port_str = ",".join(map(str, ports))
    tmp = Path(tempfile.gettempdir()) / f"nmap_svc_{scan_id}.xml"
    output_file = str(tmp)

    try:
        nmap_path = config.get("tools", {}).get("nmap", "nmap")
        cmd = [nmap_path, "-sV", "-p", port_str, "-Pn", "-oX", output_file, target]
        subprocess.run(cmd, capture_output=True, text=True, check=False)

        if tmp.exists():
            results.append({
                "host": target,
                "nmap_xml": output_file,
                "scan_id": scan_id,
            })
    except (subprocess.SubprocessError, OSError):
        pass

    return results
