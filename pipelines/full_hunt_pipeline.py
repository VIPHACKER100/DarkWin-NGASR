"""DARKWIN Full Hunt Pipeline

End-to-end offensive security pipeline: starts with deep reconnaissance,
then fans out into web vulnerability scanning for every discovered subdomain.

Author: ARYAN AHIRWAR (VIPHACKER.100)
"""

from core.pipeline_engine import Pipeline, PipelineStep
from pipelines.recon_pipeline import get_recon_pipeline
from pipelines.web_vuln_pipeline import get_web_vuln_pipeline

# Ghost Recon module for stealth coordination
from modules.reconnaissance.ghost_recon import run as ghost_recon


def get_full_hunt_pipeline(target: str, scan_id: str, config: dict) -> Pipeline:
    """Build a full-hunt pipeline that combines recon + web scanning.

    Execution Strategy
    ------------------
    1. Ghost Recon (pre-flight)
         Initialises stealth mode, configures proxy rotation, and sets up
         rate-limiting before any active probes begin.

    2. Reconnaissance Pipeline (embedded as sub-steps)
         All steps from :func:`get_recon_pipeline` are cloned into this
         pipeline so the single engine run covers the full attack surface.

    3. Web Vulnerability Pipeline (embedded as sub-steps)
         All steps from :func:`get_web_vuln_pipeline` are cloned into this
         pipeline, targeting the root URL of the supplied target.

         In production, the orchestrator would iterate over every subdomain
         discovered in Phase 2 and spawn a web_vuln run per host – this is
         handled by the agent_loop when full_hunt mode is enabled.

    Args:
        target:  Root domain or IP (e.g. "example.com")
        scan_id: UUID of the parent Scan record
        config:  Global DarkWin config dict

    Returns:
        Fully configured Pipeline instance ready for ``pipeline.run()``.
    """
    pipeline = Pipeline("Full Hunt", [])

    # ── Pre-flight: Ghost Recon (stealth initialisation) ─────────────────────
    pipeline.add_step(PipelineStep(
        name="Ghost Recon (Stealth Init)",
        module_fn=ghost_recon,
        args=[target, scan_id, config],
        timeout_seconds=60,
        required=False,
    ))

    # ── Phase 1-3: Full Reconnaissance ───────────────────────────────────────
    recon = get_recon_pipeline(target, scan_id, config)
    for step in recon.steps:
        pipeline.add_step(step)

    # ── Phase 4-7: Web Vulnerability Scanning (root target) ──────────────────
    # Determine the web root URL from target
    scheme = "https"
    root_url = f"{scheme}://{target}"

    web = get_web_vuln_pipeline(root_url, scan_id, config)
    for step in web.steps:
        pipeline.add_step(step)

    return pipeline
