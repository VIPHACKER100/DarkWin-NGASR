import subprocess
import os
import json
from typing import List, Dict

MODULE_META = {
    "name": "API Fuzzer",
    "category": "Fuzzing",
    "description": "Fuzzes API endpoints for hidden methods and parameters",
    "version": "1.0.0"
}

def run(url: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Fuzzes an API endpoint for common patterns.
    """
    findings = []
    output_file = f"/tmp/fuzz_api_{scan_id}.json"
    if os.name == 'nt':
        output_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), f"fuzz_api_{scan_id}.json")

    wordlist = os.path.join("wordlists", "api_endpoints.txt")
    if not os.path.exists(wordlist):
        return []

    try:
        ffuf_path = config.get("tools", {}).get("ffuf", "ffuf")
        # Fuzzing methods: GET, POST, PUT, DELETE, PATCH
        for method in ["GET", "POST", "PUT", "DELETE"]:
            cmd = [
                ffuf_path, "-u", url, "-X", method, 
                "-w", wordlist, "-mc", "200,201,401,403", 
                "-o", output_file, "-of", "json"
            ]
            subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    for result in data.get("results", []):
                        findings.append({
                            "type": "api_endpoint",
                            "method": method,
                            "url": result.get("url"),
                            "status": result.get("status"),
                            "scan_id": scan_id
                        })
                os.remove(output_file)
    except Exception:
        pass
        
    return findings
