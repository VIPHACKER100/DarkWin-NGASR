"""DARKWIN Port Scanner module.

Shells out to masscan for high-speed port scanning and parses the JSON output.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "Port Scanner",
    "category": "Network",
    "description": "Shells out to masscan for high-speed port scanning",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Run masscan on the target and parse its JSON output.

    Args:
        target: Hostname or IP to scan.
        scan_id: Unique scan identifier injected into each result.
        config: Application config dict; expects
            ``config["tools"]["masscan"]`` for the binary path.

    Returns:
        A list of port dicts with keys ``ip``, ``port``, ``proto``,
        and ``scan_id``.  Returns an empty list if masscan is not
        available or the output cannot be parsed.
    """
    ports: List[Dict[str, Any]] = []
    tmp = Path(tempfile.gettempdir()) / f"masscan_{scan_id}.json"
    output_file = str(tmp)

    try:
        masscan_path = config.get("tools", {}).get("masscan", "masscan")
        cmd = [masscan_path, target, "-p1-65535", "--rate", "1000", "-oJ", output_file]
        subprocess.run(cmd, capture_output=True, text=True, check=False)

        if tmp.exists():
            with tmp.open("r", encoding="utf-8") as f:
                data: Any = json.load(f)
            for entry in data:
                for port_info in entry.get("ports", []):
                    ports.append({
                        "ip": entry.get("ip"),
                        "port": port_info.get("port"),
                        "proto": port_info.get("proto"),
                        "scan_id": scan_id,
                    })
            tmp.unlink(missing_ok=True)
    except (subprocess.SubprocessError, OSError, json.JSONDecodeError):
        pass

    return ports
