import os
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict

MODULE_META = {
    "name": "HTML Reporter",
    "category": "Reporting",
    "description": "Generates a premium HTML report with charts and tables",
    "version": "1.0.0"
}

def run(scan_results: dict, scan_id: str, config: dict) -> str:
    """
    Generates an HTML report.
    """
    output_dir = os.path.join(config.get("scans", {}).get("output_dir", "reports"), scan_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "report.html")
    
    # In a real app, we would use a Jinja2 template
    html_content = f"""
    <html>
    <head>
        <title>DARKWIN Scan Report - {scan_id}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f1f5f9; padding: 20px; }}
            h1 {{ color: #38bdf8; }}
            .vulnerability {{ border: 1px solid #334155; padding: 15px; margin-bottom: 10px; border-radius: 8px; background: #1e293b; }}
            .Critical {{ border-left: 5px solid #ef4444; }}
            .High {{ border-left: 5px solid #f97316; }}
            .Medium {{ border-left: 5px solid #eab308; }}
            .Low {{ border-left: 5px solid #22c55e; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>DARKWIN Security Report</h1>
            <div>Developed by ARYAN AHIRWAR (VIPHACKER.100)</div>
        </div>
        <h2>Scan ID: {scan_id}</h2>
        <p>Target: {scan_results.get('target')}</p>
        <hr>
        <h3>Findings</h3>
        {''.join([f'<div class="vulnerability {v.get("severity")}"><b>{v.get("vuln_type").upper()}</b> - {v.get("severity")}<br>{v.get("description")}<br><i>{v.get("endpoint")}</i></div>' for v in scan_results.get('findings', [])])}
    </body>
    </html>
    """
    
    with open(output_file, 'w') as f:
        f.write(html_content)
        
    return output_file
