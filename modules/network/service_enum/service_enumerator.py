import subprocess
import os
from typing import List, Dict

MODULE_META = {
    "name": "Service Enumerator",
    "category": "Network",
    "description": "Uses nmap for detailed service and version enumeration",
    "version": "1.0.0"
}

def run(target: str, ports: List[int], scan_id: str, config: dict) -> List[Dict]:
    """
    Runs nmap for service detection on specific ports.
    """
    results = []
    port_str = ",".join(map(str, ports))
    
    output_file = f"/tmp/nmap_svc_{scan_id}.xml"
    if os.name == 'nt':
        output_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), f"nmap_svc_{scan_id}.xml")

    try:
        # nmap -sV -p<ports> -Pn -oX <output_file> <target>
        nmap_path = config.get("tools", {}).get("nmap", "nmap")
        cmd = [nmap_path, "-sV", "-p", port_str, "-Pn", "-oX", output_file, target]
        subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(output_file):
            results.append({
                "host": target,
                "nmap_xml": output_file,
                "scan_id": scan_id
            })
    except Exception:
        pass
        
    return results
