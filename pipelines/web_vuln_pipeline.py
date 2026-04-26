from core.pipeline_engine import Pipeline, PipelineStep
from modules.web_scanning.crawler_engine.crawler import run as crawler
from modules.vulnerability_engine.web.xss.xss_scanner import run as xss
from modules.vulnerability_engine.web.csrf.csrf_scanner import run as csrf

def get_web_vuln_pipeline(url: str, scan_id: str, config: dict) -> Pipeline:
    pipeline = Pipeline("Web Vulnerability Scan", [])
    
    # Step 1: Crawling
    # Note: async modules would need special handling in the engine
    # pipeline.add_step(PipelineStep("Crawler", crawler, [url, scan_id, config]))
    
    # Step 2: Vulnerability Scanning
    pipeline.add_step(PipelineStep("XSS Scan", xss, [url, scan_id, config]))
    pipeline.add_step(PipelineStep("CSRF Scan", csrf, [url, scan_id, config]))
    
    return pipeline
