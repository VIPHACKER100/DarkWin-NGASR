"""DARKWIN Subfinder Runner module.

Shells out to subfinder for passive subdomain discovery.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import subprocess
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "Subfinder Runner",
    "category": "Reconnaissance",
    "description": "Shells out to subfinder for passive subdomain discovery",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Run subfinder on the target and return discovered subdomains.

    Args:
        target: Domain to enumerate.
        scan_id: Unique scan identifier.
        config: Application config; expects ``config["tools"]["subfinder"]``.

    Returns:
        List of subdomain dicts, or empty on failure.
    """
    subdomains: List[Dict[str, Any]] = []

    try:
        subfinder_path = config.get("tools", {}).get("subfinder", "subfinder")
        cmd = [subfinder_path, "-d", target, "-silent", "-json"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, _ = process.communicate()

        if process.returncode == 0:
            for line in stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data: Any = json.loads(line)
                    subdomains.append({
                        "subdomain": data.get("host"),
                        "source": "subfinder",
                        "scan_id": scan_id,
                    })
                except json.JSONDecodeError:
                    continue
    except (subprocess.SubprocessError, OSError):
        pass

    return subdomains
