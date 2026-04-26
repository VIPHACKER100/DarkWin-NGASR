import os
from typing import List, Dict

MODULE_META = {
    "name": "Markdown Reporter",
    "category": "Reporting",
    "description": "Generates a clean Markdown report suitable for GitHub or Obsidian",
    "version": "1.0.0"
}

def run(scan_results: dict, scan_id: str, config: dict) -> str:
    """
    Generates a Markdown report.
    """
    output_dir = os.path.join(config.get("scans", {}).get("output_dir", "reports"), scan_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "report.md")
    
    md_content = f"""# DARKWIN Scan Report
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

**Scan ID:** {scan_id}
**Target:** {scan_results.get('target')}
**Date:** {scan_results.get('date')}

---

### Summary
- Total Findings: {len(scan_results.get('findings', []))}
- Critical: {len([v for v in scan_results.get('findings', []) if v.get('severity') == 'Critical'])}
- High: {len([v for v in scan_results.get('findings', []) if v.get('severity') == 'High'])}

### Findings
"""
    for v in scan_results.get('findings', []):
        md_content += f"""
#### [{v.get('severity')}] {v.get('vuln_type').upper()}
- **Endpoint:** `{v.get('endpoint')}`
- **Description:** {v.get('description')}
- **Payload:** `{v.get('payload')}`
"""
    
    with open(output_file, 'w') as f:
        f.write(md_content)
        
    return output_file
