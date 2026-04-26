import subprocess
import json
import os
from typing import List, Dict

MODULE_META = {
    "name": "Endpoint Finder",
    "category": "Web Scanning",
    "description": "Uses ffuf to brute-force directories and files",
    "version": "1.0.0"
}

def run(url: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Runs ffuf to find hidden directories and files.
    """
    endpoints = []
    output_file = f"/tmp/dirs_{scan_id}.json"
    if os.name == 'nt':
        output_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), f"dirs_{scan_id}.json")

    wordlist = os.path.join("wordlists", "directories.txt")
    if not os.path.exists(wordlist):
        return []

    try:
        # ffuf -u <url>/FUZZ -w <wordlist> -mc 200,301,302,403 -o <output_file> -of json
        ffuf_path = config.get("tools", {}).get("ffuf", "ffuf")
        cmd = [
            ffuf_path, "-u", f"{url.rstrip('/')}/FUZZ", 
            "-w", wordlist, "-mc", "200,301,302,403", 
            "-o", output_file, "-of", "json"
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                data = json.load(f)
                for result in data.get("results", []):
                    endpoints.append({
                        "endpoint": result.get("url"),
                        "status_code": result.get("status"),
                        "scan_id": scan_id
                    })
            os.remove(output_file)
    except Exception:
        pass
        
    return endpoints
