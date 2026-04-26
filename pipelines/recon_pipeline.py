from core.pipeline_engine import Pipeline, PipelineStep
from modules.reconnaissance.subdomain.subfinder_runner import run as subfinder
from modules.reconnaissance.subdomain.crt_sh_fetcher import run as crt_sh
from modules.reconnaissance.dns.dns_enum import run as dns_enum

def get_recon_pipeline(target: str, scan_id: str, config: dict) -> Pipeline:
    pipeline = Pipeline("Reconnaissance", [])
    
    # Step 1: Subdomain Discovery
    pipeline.add_step(PipelineStep("Subfinder", subfinder, [target, scan_id, config]))
    pipeline.add_step(PipelineStep("crt.sh", crt_sh, [target, scan_id, config]))
    
    # Step 2: DNS Enumeration
    pipeline.add_step(PipelineStep("DNS Enum", dns_enum, [target, scan_id, config]))
    
    return pipeline
