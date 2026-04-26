from core.database import SessionLocal
from core.models import Scan, Finding
from pipelines.recon_pipeline import ReconPipeline
from pipelines.scan_pipeline import ScanPipeline
import time
import uuid

def watch_target(domain: str, interval_hours: int = 24):
    """
    Continuously monitors a target for changes and new vulnerabilities.
    """
    while True:
        scan_id = str(uuid.uuid4())
        print(f"[*] Starting 'Watch' cycle for {domain} (Scan ID: {scan_id})")
        
        # 1. Run Recon to find new assets
        recon = ReconPipeline(domain)
        recon.run(domain, scan_id)
        
        # 2. Logic to diff with previous scan would go here
        # For now, we run the scan on any findings from recon
        
        # 3. Run Vulnerability Scan
        scanner = ScanPipeline(domain)
        scanner.run(domain, scan_id)
        
        print(f"[+] 'Watch' cycle complete for {domain}. Sleeping for {interval_hours} hours.")
        time.sleep(interval_hours * 3600)
