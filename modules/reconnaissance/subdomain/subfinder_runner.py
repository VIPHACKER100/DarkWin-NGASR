import subprocess
import json
import os
from typing import List, Dict

MODULE_META = {
    "name": "Subfinder Runner",
    "category": "Reconnaissance",
    "description": "Shells out to subfinder for passive subdomain discovery",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Runs subfinder on the target and returns discovered subdomains.
    """
    subdomains = []
    try:
        # subfinder -d <target> -silent -json
        cmd = [config.get("tools", {}).get("subfinder", "subfinder"), "-d", target, "-silent", "-json"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            for line in stdout.splitlines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        subdomains.append({
                            "subdomain": data.get("host"),
                            "source": "subfinder",
                            "scan_id": scan_id
                        })
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        # In a real app, log the error
        pass
    
    return subdomains
