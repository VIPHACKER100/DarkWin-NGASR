"""DARKWIN Reconnaissance Pipeline

Phase-aware pipeline that orchestrates all available recon modules in
parallel waves: subdomain discovery → DNS + WHOIS + Dorking → port/SSL analysis.

Author: ARYAN AHIRWAR (VIPHACKER.100)
"""

from core.pipeline_engine import Pipeline, PipelineStep

# --- Subdomain Discovery ---
from modules.reconnaissance.subdomain.subfinder_runner import run as subfinder
from modules.reconnaissance.subdomain.crt_sh_fetcher import run as crt_sh
from modules.reconnaissance.subdomain.amass_runner import run as amass
from modules.reconnaissance.subdomain.bruteforce_subdomains import run as brute_sub

# --- DNS & WHOIS ---
from modules.reconnaissance.dns.dns_enum import run as dns_enum
from modules.reconnaissance.whois.whois_lookup import run as whois

# --- Search Engine Dorking ---
from modules.reconnaissance.search_engine_dorking.dork_engine import run as dork

# --- Network: Port Scan & SSL ---
from modules.network.port_scan.port_scanner import run as port_scan
from modules.network.ssl_analysis.ssl_analyzer import run as ssl_analyze


def get_recon_pipeline(target: str, scan_id: str, config: dict) -> Pipeline:
    """Build a full reconnaissance pipeline for the given target.

    Execution order (all steps within a phase run in parallel via the engine):

      Phase 1 – Subdomain Discovery
        • Subfinder       – passive API-based enumeration
        • crt.sh          – certificate transparency log search
        • Amass           – graph-based passive/active enum
        • Bruteforce      – wordlist-driven subdomain brute-force

      Phase 2 – Intelligence Gathering
        • DNS Enum        – A / MX / NS / TXT / SPF record enumeration
        • WHOIS Lookup    – registrar, org, and ASN metadata
        • Dork Engine     – Google/Bing dork-based exposure discovery

      Phase 3 – Network Profiling
        • Port Scanner    – top-1000 TCP/UDP port sweep via nmap
        • SSL Analyzer    – cipher strength, cert chain, and expiry checks

    Args:
        target:  Target domain or IP address
        scan_id: UUID of the parent Scan record
        config:  Global DarkWin config dict

    Returns:
        Configured Pipeline instance ready to execute.
    """
    pipeline = Pipeline("Reconnaissance", [])

    # ── Phase 1: Subdomain Discovery (passive + active) ───────────────────────
    pipeline.add_step(PipelineStep(
        name="Subfinder",
        module_fn=subfinder,
        args=[target, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="crt.sh",
        module_fn=crt_sh,
        args=[target, scan_id, config],
        timeout_seconds=120,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="Amass",
        module_fn=amass,
        args=[target, scan_id, config],
        timeout_seconds=600,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="Subdomain Bruteforce",
        module_fn=brute_sub,
        args=[target, scan_id, config],
        timeout_seconds=900,
        required=False,
    ))

    # ── Phase 2: Intelligence Gathering ──────────────────────────────────────
    pipeline.add_step(PipelineStep(
        name="DNS Enumeration",
        module_fn=dns_enum,
        args=[target, scan_id, config],
        timeout_seconds=180,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="WHOIS Lookup",
        module_fn=whois,
        args=[target, scan_id, config],
        timeout_seconds=60,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="Dork Engine",
        module_fn=dork,
        args=[target, scan_id, config],
        timeout_seconds=120,
        required=False,
    ))

    # ── Phase 3: Network Profiling ────────────────────────────────────────────
    pipeline.add_step(PipelineStep(
        name="Port Scanner",
        module_fn=port_scan,
        args=[target, scan_id, config],
        timeout_seconds=600,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="SSL Analyzer",
        module_fn=ssl_analyze,
        args=[target, scan_id, config],
        timeout_seconds=120,
        required=False,
    ))

    return pipeline
