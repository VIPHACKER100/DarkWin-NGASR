import subprocess
import os
import json
from typing import List, Dict

MODULE_META = {
    "name": "Parameter Fuzzer",
    "category": "Fuzzing",
    "description": "Intensively fuzzes parameters for hidden functionality",
    "version": "1.0.0"
}

def run(url: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Runs ffuf for intensive parameter fuzzing.
    """
    findings = []
    output_file = f"/tmp/fuzz_params_{scan_id}.json"
    if os.name == 'nt':
        output_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), f"fuzz_params_{scan_id}.json")

    wordlist = os.path.join("wordlists", "parameters_large.txt")
    if not os.path.exists(wordlist):
        wordlist = os.path.join("wordlists", "parameters.txt")
        if not os.path.exists(wordlist):
            return []

    try:
        ffuf_path = config.get("tools", {}).get("ffuf", "ffuf")
        cmd = [
            ffuf_path, "-u", f"{url}?FUZZ=1", 
            "-w", wordlist, "-mc", "200,301,302,403", 
            "-o", output_file, "-of", "json"
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                data = json.load(f)
                for result in data.get("results", []):
                    findings.append({
                        "type": "parameter",
                        "parameter": result.get("input").get("FUZZ"),
                        "url": result.get("url"),
                        "status": result.get("status"),
                        "scan_id": scan_id
                    })
            os.remove(output_file)
    except Exception:
        pass
        
    return findings
