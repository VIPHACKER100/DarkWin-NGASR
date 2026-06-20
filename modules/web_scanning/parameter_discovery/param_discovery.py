"""DARKWIN Parameter Discovery module.

Uses ffuf to discover hidden URL parameters on a given endpoint.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from core.logging_system import get_logger

logger = get_logger("WebScanning.ParameterDiscovery")

MODULE_META: Dict[str, str] = {
    "name": "Parameter Discovery",
    "category": "Web Scanning",
    "description": "Uses ffuf to discover hidden URL parameters",
    "version": "1.0.0",
}


def run(url: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Run ffuf to discover hidden URL parameters.

    Args:
        url: Target URL.
        scan_id: Unique scan identifier.
        config: Application config; expects ``config["tools"]["ffuf"]``.

    Returns:
        List of discovered parameter dicts.
    """
    params: List[Dict[str, Any]] = []
    tmp = Path(tempfile.gettempdir()) / f"params_{scan_id}.json"
    output_file = str(tmp)

    wordlist = Path("wordlists") / "parameters.txt"
    if not wordlist.exists():
        logger.error(f"Wordlist not found: {wordlist}")
        return []

    try:
        ffuf_path = config.get("tools", {}).get("ffuf", "ffuf")
        cmd = [
            ffuf_path, "-u", f"{url}?FUZZ=test",
            "-w", str(wordlist), "-mc", "200,301,302",
            "-o", output_file, "-of", "json",
        ]
        logger.info(f"Running ffuf: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error(f"ffuf failed: {result.stderr}")

        if tmp.exists():
            with tmp.open("r", encoding="utf-8") as f:
                try:
                    data: Any = json.load(f)
                    for entry in data.get("results", []):
                        params.append({
                            "parameter": entry.get("input", {}).get("FUZZ"),
                            "url": url,
                            "scan_id": scan_id,
                        })
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing ffuf output: {e}")
            tmp.unlink(missing_ok=True)
    except subprocess.SubprocessError as e:
        logger.error(f"ffuf execution error: {e}")
    except OSError as e:
        logger.error(f"File system error in parameter discovery: {e}")

    return params
