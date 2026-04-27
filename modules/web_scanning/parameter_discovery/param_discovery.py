
import subprocess
import json
import os
from typing import List, Dict, Any
from core.logging_system import get_logger

logger = get_logger("WebScanning.ParameterDiscovery")

MODULE_META = {
    "name": "Parameter Discovery",
    "category": "Web Scanning",
    "description": "Uses ffuf to discover hidden URL parameters",
    "version": "1.0.0"
}

def run(url: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """
    Runs ffuf to find hidden parameters for a given URL with error handling and logging.
    """
    params: List[Dict[str, Any]] = []
    output_file = f"/tmp/params_{scan_id}.json"
    if os.name == 'nt':
        output_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), f"params_{scan_id}.json")

    wordlist = os.path.join("wordlists", "parameters.txt")
    if not os.path.exists(wordlist):
        logger.error(f"Wordlist not found: {wordlist}")
        return []

    try:
        ffuf_path = config.get("tools", {}).get("ffuf", "ffuf")
        cmd = [
            ffuf_path, "-u", f"{url}?FUZZ=test",
            "-w", wordlist, "-mc", "200,301,302",
            "-o", output_file, "-of", "json"
        ]
        logger.info(f"Running ffuf: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error(f"ffuf failed: {result.stderr}")
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                try:
                    data = json.load(f)
                    for result in data.get("results", []):
                        params.append({
                            "parameter": result.get("input", {}).get("FUZZ"),
                            "url": url,
                            "scan_id": scan_id
                        })
                except Exception as e:
                    logger.error(f"Error parsing ffuf output: {e}")
            os.remove(output_file)
    except Exception as e:
        logger.critical(f"Unexpected error in parameter discovery: {e}")
    return params
