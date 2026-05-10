from core.database import SessionLocal
from core.models import Scan, Finding
from pipelines.recon_pipeline import get_recon_pipeline
from pipelines.web_vuln_pipeline import get_web_vuln_pipeline
from core.config_manager import get_config
import time
import uuid

def watch_target(domain: str, interval_hours: int = 24):
    """
    Continuously monitors a target for changes and new vulnerabilities.
    """
    config = get_config().dict()
    while True:
        scan_id = str(uuid.uuid4())
        print(f"[*] Starting 'Watch' cycle for {domain} (Scan ID: {scan_id})")
        
        # 1. Run Recon to find new assets
        recon_pipeline = get_recon_pipeline(domain, scan_id, config)
        recon_pipeline.run(domain, scan_id)
        
        # 2. Logic to diff with previous scan would go here
        # For now, we run the scan on any findings from recon
        
        # 3. Run Vulnerability Scan
        root_url = f"https://{domain}"
        vuln_pipeline = get_web_vuln_pipeline(root_url, scan_id, config)
        vuln_pipeline.run(domain, scan_id)
        
        print(f"[+] 'Watch' cycle complete for {domain}. Sleeping for {interval_hours} hours.")
        time.sleep(interval_hours * 3600)
