import subprocess
import json
import os
from typing import List, Dict

MODULE_META = {
    "name": "Amass Runner",
    "category": "Reconnaissance",
    "description": "Shells out to amass for passive subdomain discovery",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Runs amass enum -passive -d <target> -json and returns subdomains.
    """
    subdomains = []
    output_file = f"/tmp/amass_{scan_id}.json"
    if os.name == 'nt':
        output_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), f"amass_{scan_id}.json")

    try:
        # amass enum -passive -d <target> -json <output_file>
        cmd = [
            config.get("tools", {}).get("amass", "amass"), 
            "enum", "-passive", "-d", target, "-json", output_file
        ]
        subprocess.run(cmd, capture_output=True, text=True)

        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            subdomains.append({
                                "subdomain": data.get("name"),
                                "source": "amass",
                                "scan_id": scan_id
                            })
                        except json.JSONDecodeError:
                            continue
            os.remove(output_file)
    except Exception as e:
        pass
    
    return subdomains
