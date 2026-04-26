import subprocess
import os
from typing import List, Dict

MODULE_META = {
    "name": "Port Scanner",
    "category": "Network",
    "description": "Shells out to masscan for high-speed port scanning",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Runs masscan on the target.
    """
    ports = []
    output_file = f"/tmp/masscan_{scan_id}.json"
    if os.name == 'nt':
        output_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), f"masscan_{scan_id}.json")

    try:
        # masscan <target> -p1-65535 --rate 1000 -oJ <output_file>
        masscan_path = config.get("tools", {}).get("masscan", "masscan")
        cmd = [
            masscan_path, target, "-p1-65535", 
            "--rate", "1000", "-oJ", output_file
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(output_file):
            import json
            with open(output_file, 'r') as f:
                data = json.load(f)
                for entry in data:
                    for port_info in entry.get("ports", []):
                        ports.append({
                            "ip": entry.get("ip"),
                            "port": port_info.get("port"),
                            "proto": port_info.get("proto"),
                            "scan_id": scan_id
                        })
            os.remove(output_file)
    except Exception:
        pass
        
    return ports
