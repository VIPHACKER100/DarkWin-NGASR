import subprocess
import os
import json
from typing import List, Dict

MODULE_META = {
    "name": "SSL Analyzer",
    "category": "Network",
    "description": "Analyzes SSL/TLS configuration for vulnerabilities using testssl.sh",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Runs testssl.sh or equivalent for SSL analysis.
    """
    findings = []
    output_file = f"/tmp/testssl_{scan_id}.json"
    if os.name == 'nt':
        output_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), f"testssl_{scan_id}.json")

    try:
        # testssl.sh --jsonfile <output_file> <target>
        # Note: testssl.sh is often a script, so we assume it's in the path
        cmd = ["testssl.sh", "--jsonfile", output_file, target]
        subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                data = json.load(f)
                for entry in data:
                    if entry.get("severity") in ["HIGH", "CRITICAL"]:
                        findings.append({
                            "vuln_type": "ssl_misconfig",
                            "severity": entry.get("severity").capitalize(),
                            "endpoint": target,
                            "description": entry.get("finding"),
                            "scan_id": scan_id
                        })
            os.remove(output_file)
    except Exception:
        pass
        
    return findings
