import subprocess
import json
import os
from typing import List, Dict

MODULE_META = {
    "name": "Parameter Discovery",
    "category": "Web Scanning",
    "description": "Uses ffuf to discover hidden URL parameters",
    "version": "1.0.0"
}

def run(url: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Runs ffuf to find hidden parameters for a given URL.
    """
    params = []
    output_file = f"/tmp/params_{scan_id}.json"
    if os.name == 'nt':
        output_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), f"params_{scan_id}.json")

    wordlist = os.path.join("wordlists", "parameters.txt")
    if not os.path.exists(wordlist):
        return []

    try:
        # ffuf -u <url>?FUZZ=test -w <wordlist> -mc 200,301,302 -o <output_file> -of json
        ffuf_path = config.get("tools", {}).get("ffuf", "ffuf")
        cmd = [
            ffuf_path, "-u", f"{url}?FUZZ=test", 
            "-w", wordlist, "-mc", "200,301,302", 
            "-o", output_file, "-of", "json"
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                data = json.load(f)
                for result in data.get("results", []):
                    params.append({
                        "parameter": result.get("input").get("FUZZ"),
                        "url": url,
                        "scan_id": scan_id
                    })
            os.remove(output_file)
    except Exception:
        pass
        
    return params
