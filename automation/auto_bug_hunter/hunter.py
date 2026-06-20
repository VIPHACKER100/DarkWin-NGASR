"""DARKWIN Auto Bug Hunter module.

Continuously monitors a target domain for changes and new vulnerabilities
by cycling through recon and web vulnerability pipelines at a configurable interval.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import time
import uuid

from core.config_manager import get_config
from core.database import SessionLocal
from core.models import Scan, Finding
from pipelines.recon_pipeline import get_recon_pipeline
from pipelines.web_vuln_pipeline import get_web_vuln_pipeline


def watch_target(domain: str, interval_hours: int = 24) -> None:
    """Continuously monitor a target for changes and new vulnerabilities.

    Args:
        domain: Target domain to monitor.
        interval_hours: Pause between watch cycles (default 24).
    """
    config = get_config().dict()
    while True:
        scan_id = str(uuid.uuid4())
        print(f"[*] Starting 'Watch' cycle for {domain} (Scan ID: {scan_id})")

        recon_pipeline = get_recon_pipeline(domain, scan_id, config)
        recon_pipeline.run(domain, scan_id)

        root_url = f"https://{domain}"
        vuln_pipeline = get_web_vuln_pipeline(root_url, scan_id, config)
        vuln_pipeline.run(domain, scan_id)

        print(f"[+] 'Watch' cycle complete for {domain}. Sleeping for {interval_hours} hours.")
        time.sleep(interval_hours * 3600)
