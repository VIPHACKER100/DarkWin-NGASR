"""DARKWIN Endpoint Finder module.

Uses ffuf to brute-force hidden directories and files on a web target.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "Endpoint Finder",
    "category": "Web Scanning",
    "description": "Uses ffuf to brute-force directories and files",
    "version": "1.0.0",
}


def run(url: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Run ffuf to discover hidden directories and files.

    Args:
        url: Target URL.
        scan_id: Unique scan identifier.
        config: Application config; expects ``config["tools"]["ffuf"]``.

    Returns:
        List of endpoint dicts, or empty on failure.
    """
    endpoints: List[Dict[str, Any]] = []
    tmp = Path(tempfile.gettempdir()) / f"dirs_{scan_id}.json"
    output_file = str(tmp)

    wordlist = Path("wordlists") / "directories.txt"
    if not wordlist.exists():
        return []

    try:
        ffuf_path = config.get("tools", {}).get("ffuf", "ffuf")
        cmd = [
            ffuf_path, "-u", f"{url.rstrip('/')}/FUZZ",
            "-w", str(wordlist), "-mc", "200,301,302,403",
            "-o", output_file, "-of", "json",
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=False)

        if tmp.exists():
            with tmp.open("r", encoding="utf-8") as f:
                data: Any = json.load(f)
            for result in data.get("results", []):
                endpoints.append({
                    "endpoint": result.get("url"),
                    "status_code": result.get("status"),
                    "scan_id": scan_id,
                })
            tmp.unlink(missing_ok=True)
    except (subprocess.SubprocessError, OSError, json.JSONDecodeError):
        pass

    return endpoints
