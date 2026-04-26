import json
import os
from typing import List, Dict

MODULE_META = {
    "name": "Attack Graph Generator",
    "category": "Reporting",
    "description": "Generates a visual attack graph linking subdomains, services, and vulnerabilities",
    "version": "1.0.0"
}

def run(scan_results: dict, scan_id: str, config: dict) -> str:
    """
    Generates a Mermaid-style attack graph.
    """
    output_dir = os.path.join(config.get("scans", {}).get("output_dir", "reports"), scan_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "attack_graph.md")
    
    graph_content = "graph TD\n"
    target = scan_results.get("target", "Target")
    graph_content += f"    Root({target}) --> Subdomains\n"
    
    for v in scan_results.get("findings", []):
        endpoint = v.get("endpoint", "endpoint")
        vuln = v.get("vuln_type", "vulnerability")
        graph_content += f"    Subdomains --> {endpoint}\n"
        graph_content += f"    {endpoint} --> {vuln}(({vuln}))\n"
        if v.get("severity") in ["Critical", "High"]:
            graph_content += f"    style {vuln} fill:#f96,stroke:#333,stroke-width:4px\n"
            
    with open(output_file, 'w') as f:
        f.write(f"```mermaid\n{graph_content}\n```")
        
    return output_file
