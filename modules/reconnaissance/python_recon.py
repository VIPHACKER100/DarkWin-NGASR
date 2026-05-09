import asyncio
import socket
import httpx
from typing import List, Dict
from core.logging_system import get_logger

logger = get_logger("PythonRecon")

MODULE_META = {
    "name": "Python Recon (Light)",
    "category": "Reconnaissance",
    "description": "Pure Python reconnaissance: Port scanning, HTTP header analysis, and basic enumeration without external binaries.",
    "version": "1.0.0"
}

async def scan_port(host: str, port: int) -> bool:
    """Check if a port is open."""
    try:
        conn = asyncio.open_connection(host, port)
        await asyncio.wait_for(conn, timeout=1.0)
        return True
    except:
        return False

async def analyze_headers(url: str) -> List[Dict]:
    """Analyze HTTP headers for interesting info."""
    findings = []
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            resp = await client.get(url)
            headers = resp.headers
            
            # Check for server header
            server = headers.get("Server")
            if server:
                findings.append({
                    "vuln_type": "info",
                    "severity": "Info",
                    "endpoint": url,
                    "description": f"Server header discovered: {server}",
                    "scan_id": "RECON"
                })
                
            # Check for missing security headers
            security_headers = ["Content-Security-Policy", "X-Frame-Options", "Strict-Transport-Security"]
            for sh in security_headers:
                if sh not in headers:
                    findings.append({
                        "vuln_type": "missing_header",
                        "severity": "Low",
                        "endpoint": url,
                        "description": f"Missing security header: {sh}",
                        "scan_id": "RECON"
                    })
    except Exception as e:
        logger.debug(f"Header analysis failed for {url}: {e}")
    return findings

async def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Main entry point for Python Recon.
    """
    logger.info(f"Starting Python-native reconnaissance on {target}")
    findings = []
    
    # 1. Basic Port Scan (common ports)
    common_ports = [80, 443, 8080, 8443, 21, 22, 25, 3306, 5432]
    open_ports = []
    
    # Resolve host
    try:
        host = socket.gethostbyname(target)
    except:
        host = target

    for port in common_ports:
        if await scan_port(host, port):
            open_ports.append(port)
            findings.append({
                "vuln_type": "port",
                "severity": "Info",
                "endpoint": f"{target}:{port}",
                "description": f"Open port discovered via Python scan: {port}",
                "scan_id": scan_id
            })

    # 2. Header Analysis for web ports
    for port in open_ports:
        if port in [80, 443, 8080, 8443]:
            proto = "https" if port in [443, 8443] else "http"
            url = f"{proto}://{target}"
            if port not in [80, 443]:
                url += f":{port}"
            
            header_findings = await analyze_headers(url)
            for hf in header_findings:
                hf["scan_id"] = scan_id
                findings.append(hf)
                
    return findings
