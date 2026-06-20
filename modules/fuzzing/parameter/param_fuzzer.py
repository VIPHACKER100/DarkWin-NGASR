"""DARKWIN Parameter Fuzzer module.

Uses ffuf for intensive parameter fuzzing to discover hidden functionality.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

MODULE_META: Dict[str, str] = {
    "name": "Parameter Fuzzer",
    "category": "Fuzzing",
    "description": "Intensively fuzzes parameters for hidden functionality",
    "version": "1.0.0",
}


def run(url: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Run ffuf for parameter fuzzing.

    Args:
        url: Target URL.
        scan_id: Unique scan identifier.
        config: Application config; expects ``config["tools"]["ffuf"]``.

    Returns:
        List of discovered parameter dicts.
    """
    findings: List[Dict[str, Any]] = []
    tmp = Path(tempfile.gettempdir()) / f"fuzz_params_{scan_id}.json"
    output_file = str(tmp)

    wordlist = Path("wordlists") / "parameters_large.txt"
    if not wordlist.exists():
        wordlist = Path("wordlists") / "parameters.txt"
        if not wordlist.exists():
            return []

    try:
        ffuf_path = config.get("tools", {}).get("ffuf", "ffuf")
        cmd = [
            ffuf_path, "-u", f"{url}?FUZZ=1",
            "-w", str(wordlist), "-mc", "200,301,302,403",
            "-o", output_file, "-of", "json",
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=False)

        if tmp.exists():
            with tmp.open("r", encoding="utf-8") as f:
                data: Any = json.load(f)
            for result in data.get("results", []):
                findings.append({
                    "type": "parameter",
                    "parameter": result.get("input", {}).get("FUZZ"),
                    "url": result.get("url"),
                    "status": result.get("status"),
                    "scan_id": scan_id,
                })
            tmp.unlink(missing_ok=True)
    except (subprocess.SubprocessError, OSError, json.JSONDecodeError):
        pass

    return findings
