"""DARKWIN SSL Analyzer module.

Analyzes SSL/TLS configuration for vulnerabilities using testssl.sh.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "SSL Analyzer",
    "category": "Network",
    "description": "Analyzes SSL/TLS configuration for vulnerabilities using testssl.sh",
    "version": "1.0.0",
}


def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Run testssl.sh for SSL/TLS analysis.

    Args:
        target: Hostname or IP to test.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).

    Returns:
        List of finding dicts for HIGH/CRITICAL issues, or empty on failure.
    """
    findings: List[Dict[str, Any]] = []
    tmp = Path(tempfile.gettempdir()) / f"testssl_{scan_id}.json"
    output_file = str(tmp)

    try:
        cmd = ["testssl.sh", "--jsonfile", output_file, target]
        subprocess.run(cmd, capture_output=True, text=True, check=False)

        if tmp.exists():
            with tmp.open("r", encoding="utf-8") as f:
                data: Any = json.load(f)
            for entry in data:
                if entry.get("severity") in ["HIGH", "CRITICAL"]:
                    findings.append({
                        "vuln_type": "ssl_misconfig",
                        "severity": entry.get("severity").capitalize(),
                        "endpoint": target,
                        "description": entry.get("finding"),
                        "scan_id": scan_id,
                    })
            tmp.unlink(missing_ok=True)
    except (subprocess.SubprocessError, OSError, json.JSONDecodeError):
        pass

    return findings
