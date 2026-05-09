"""DARKWIN Web Vulnerability Pipeline

Comprehensive web-application attack pipeline covering surface mapping,
injection, logic flaws, and server-level vulnerabilities.

Author: ARYAN AHIRWAR (VIPHACKER.100)
"""

from core.pipeline_engine import Pipeline, PipelineStep

# --- Surface Mapping ---
from modules.web_scanning.crawler_engine.crawler import run as crawler
from modules.web_scanning.endpoint_finder.endpoint_finder import run as endpoint_finder
from modules.web_scanning.javascript_analyzer.js_analyzer import run as js_analyzer
from modules.web_scanning.parameter_discovery.param_discovery import run as param_discovery
from modules.web_scanning.ai_fuzzer import run as ai_fuzzer

# --- Web Vulnerabilities ---
from modules.vulnerability_engine.web.xss.xss_scanner import run as xss
from modules.vulnerability_engine.web.csrf.csrf_scanner import run as csrf
from modules.vulnerability_engine.web.open_redirect.open_redirect_scanner import run as open_redirect
from modules.vulnerability_engine.web.clickjacking.clickjacking_scanner import run as clickjacking

# --- Injection Vulnerabilities ---
from modules.vulnerability_engine.injection.sql.sqli_scanner import run as sqli
from modules.vulnerability_engine.injection.command.cmdi_scanner import run as cmdi
from modules.vulnerability_engine.injection.template.ssti_scanner import run as ssti
from modules.vulnerability_engine.injection.nosql.nosqli_scanner import run as nosql
from modules.vulnerability_engine.injection.graphql.graphql_scanner import run as graphql

# --- File Vulnerabilities ---
from modules.vulnerability_engine.file.lfi.lfi_scanner import run as lfi
from modules.vulnerability_engine.file.rfi.rfi_scanner import run as rfi
from modules.vulnerability_engine.file.upload_bypass.upload_bypass import run as upload_bypass

# --- Server Vulnerabilities ---
from modules.vulnerability_engine.server.rce.rce_scanner import run as rce


def get_web_vuln_pipeline(url: str, scan_id: str, config: dict) -> Pipeline:
    """Build a full web vulnerability pipeline for the given URL.

    Execution order (all steps within a phase run in parallel via the engine):

      Phase 1 – Attack Surface Mapping
        • Crawler              – spider all in-scope pages
        • Endpoint Finder      – discover hidden endpoints & directories
        • JS Analyzer          – extract endpoints / secrets from JS bundles
        • Parameter Discovery  – fuzz for hidden query/body parameters
        • AI Fuzzer            – AI-guided mutation fuzzing

      Phase 2 – Web Logic Vulnerabilities
        • XSS Scanner          – reflected, stored, DOM-based XSS
        • CSRF Scanner         – missing/bypassable CSRF tokens
        • Open Redirect        – parameter-based redirect abuse
        • Clickjacking         – missing X-Frame-Options / CSP

      Phase 3 – Injection Vulnerabilities
        • SQLi Scanner         – error-based, blind, and time-based SQLi
        • CMDi Scanner         – OS command injection
        • SSTI Scanner         – Server-Side Template Injection
        • NoSQLi Scanner       – MongoDB / Redis injection
        • GraphQL Scanner      – introspection & injection checks

      Phase 4 – File & Server Vulnerabilities
        • LFI Scanner          – Local File Inclusion path traversal
        • RFI Scanner          – Remote File Inclusion
        • Upload Bypass        – file-type restriction bypass
        • RCE Scanner          – Remote Code Execution fingerprinting

    Args:
        url:     Target URL (scheme + host + optional path)
        scan_id: UUID of the parent Scan record
        config:  Global DarkWin config dict

    Returns:
        Configured Pipeline instance ready to execute.
    """
    pipeline = Pipeline("Web Vulnerability Scan", [])

    # ── Phase 1: Attack Surface Mapping ──────────────────────────────────────
    pipeline.add_step(PipelineStep(
        name="Crawler",
        module_fn=crawler,
        args=[url, scan_id, config],
        timeout_seconds=600,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="Endpoint Finder",
        module_fn=endpoint_finder,
        args=[url, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="JavaScript Analyzer",
        module_fn=js_analyzer,
        args=[url, scan_id, config],
        timeout_seconds=180,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="Parameter Discovery",
        module_fn=param_discovery,
        args=[url, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="AI Fuzzer",
        module_fn=ai_fuzzer,
        args=[url, scan_id, config],
        timeout_seconds=600,
        required=False,
    ))

    # ── Phase 2: Web Logic Vulnerabilities ────────────────────────────────────
    pipeline.add_step(PipelineStep(
        name="XSS Scanner",
        module_fn=xss,
        args=[url, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="CSRF Scanner",
        module_fn=csrf,
        args=[url, scan_id, config],
        timeout_seconds=180,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="Open Redirect Scanner",
        module_fn=open_redirect,
        args=[url, scan_id, config],
        timeout_seconds=180,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="Clickjacking Scanner",
        module_fn=clickjacking,
        args=[url, scan_id, config],
        timeout_seconds=60,
        required=False,
    ))

    # ── Phase 3: Injection Vulnerabilities ───────────────────────────────────
    pipeline.add_step(PipelineStep(
        name="SQL Injection Scanner",
        module_fn=sqli,
        args=[url, scan_id, config],
        timeout_seconds=600,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="Command Injection Scanner",
        module_fn=cmdi,
        args=[url, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="SSTI Scanner",
        module_fn=ssti,
        args=[url, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="NoSQL Injection Scanner",
        module_fn=nosql,
        args=[url, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="GraphQL Scanner",
        module_fn=graphql,
        args=[url, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))

    # ── Phase 4: File & Server Vulnerabilities ───────────────────────────────
    pipeline.add_step(PipelineStep(
        name="LFI Scanner",
        module_fn=lfi,
        args=[url, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="RFI Scanner",
        module_fn=rfi,
        args=[url, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="Upload Bypass Scanner",
        module_fn=upload_bypass,
        args=[url, scan_id, config],
        timeout_seconds=300,
        required=False,
    ))
    pipeline.add_step(PipelineStep(
        name="RCE Scanner",
        module_fn=rce,
        args=[url, scan_id, config],
        timeout_seconds=600,
        required=False,
    ))

    return pipeline
