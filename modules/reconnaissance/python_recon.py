"""DARKWIN Python Recon (Light) module.

Pure-Python reconnaissance: port scanning, HTTP header analysis, and basic
enumeration without external binaries.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import asyncio
import socket
from typing import Any, Dict, List

import httpx

from core.logging_system import get_logger

logger = get_logger("PythonRecon")

MODULE_META: Dict[str, str] = {
    "name": "Python Recon (Light)",
    "category": "Reconnaissance",
    "description": (
        "Pure Python reconnaissance: Port scanning, HTTP header analysis, "
        "and basic enumeration without external binaries."
    ),
    "version": "1.0.0",
}


async def scan_port(host: str, port: int) -> bool:
    """Check if a TCP port is open.

    Args:
        host: Resolved IP address.
        port: Port number to probe.

    Returns:
        True if the port accepts a connection within 1 second.
    """
    try:
        conn = asyncio.open_connection(host, port)
        await asyncio.wait_for(conn, timeout=1.0)
        return True
    except (OSError, asyncio.TimeoutError):
        return False


async def analyze_headers(url: str) -> List[Dict[str, Any]]:
    """Analyze HTTP response headers for information disclosure and missing security headers.

    Args:
        url: Fully qualified URL to fetch.

    Returns:
        List of finding dicts.
    """
    findings: List[Dict[str, Any]] = []
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            resp = await client.get(url)
            headers = resp.headers

            server = headers.get("Server")
            if server:
                findings.append({
                    "vuln_type": "info",
                    "severity": "Info",
                    "endpoint": url,
                    "description": f"Server header discovered: {server}",
                    "scan_id": "RECON",
                })

            for sh in ("Content-Security-Policy", "X-Frame-Options", "Strict-Transport-Security"):
                if sh not in headers:
                    findings.append({
                        "vuln_type": "missing_header",
                        "severity": "Low",
                        "endpoint": url,
                        "description": f"Missing security header: {sh}",
                        "scan_id": "RECON",
                    })
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.debug(f"Header analysis failed for {url}: {e}")
    return findings


async def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Run Python-native reconnaissance on a target.

    Steps performed:
        1. Resolve hostname to IP.
        2. Scan common ports (80, 443, 8080, 8443, 21, 22, 25, 3306, 5432).
        3. Analyse HTTP headers on open web ports.

    Args:
        target: Hostname or IP.
        scan_id: Unique scan identifier.
        config: Application config (unused).

    Returns:
        List of finding dicts.
    """
    logger.info(f"Starting Python-native reconnaissance on {target}")
    findings: List[Dict[str, Any]] = []
    common_ports = [80, 443, 8080, 8443, 21, 22, 25, 3306, 5432]
    open_ports: List[int] = []

    try:
        host = socket.gethostbyname(target)
    except (socket.gaierror, OSError):
        host = target

    for port in common_ports:
        if await scan_port(host, port):
            open_ports.append(port)
            findings.append({
                "vuln_type": "port",
                "severity": "Info",
                "endpoint": f"{target}:{port}",
                "description": f"Open port discovered via Python scan: {port}",
                "scan_id": scan_id,
            })

    for port in open_ports:
        if port in (80, 443, 8080, 8443):
            proto = "https" if port in (443, 8443) else "http"
            url = f"{proto}://{target}"
            if port not in (80, 443):
                url += f":{port}"
            for hf in await analyze_headers(url):
                hf["scan_id"] = scan_id
                findings.append(hf)

    return findings
