"""DARKWIN Amass Runner module.

Shells out to amass for passive subdomain discovery.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "Amass Runner",
    "category": "Reconnaissance",
    "description": "Shells out to amass for passive subdomain discovery",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Run amass enum -passive against a target.

    Args:
        target: Domain to enumerate.
        scan_id: Unique scan identifier.
        config: Application config; expects ``config["tools"]["amass"]``.

    Returns:
        List of subdomain dicts, or empty on failure.
    """
    subdomains: List[Dict[str, Any]] = []
    tmp = Path(tempfile.gettempdir()) / f"amass_{scan_id}.json"
    output_file = str(tmp)

    try:
        amass_path = config.get("tools", {}).get("amass", "amass")
        cmd = [amass_path, "enum", "-passive", "-d", target, "-json", output_file]
        subprocess.run(cmd, capture_output=True, text=True, check=False)

        if tmp.exists():
            with tmp.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data: Any = json.loads(line)
                        subdomains.append({
                            "subdomain": data.get("name"),
                            "source": "amass",
                            "scan_id": scan_id,
                        })
                    except json.JSONDecodeError:
                        continue
            tmp.unlink(missing_ok=True)
    except (subprocess.SubprocessError, OSError):
        pass

    return subdomains
