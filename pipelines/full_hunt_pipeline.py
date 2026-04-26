from pipelines.recon_pipeline import get_recon_pipeline
from pipelines.web_vuln_pipeline import get_web_vuln_pipeline
from core.pipeline_engine import Pipeline

def get_full_hunt_pipeline(target: str, scan_id: str, config: dict) -> Pipeline:
    """
    Combines recon and web scans into a full hunt pipeline.
    """
    recon = get_recon_pipeline(target, scan_id, config)
    # Full hunt would iterate over discovered subdomains
    return recon
