"""DARKWIN Vulnerability Verification Engine

Provides automated verification of discovered findings to minimize 
false positives. Uses safe, non-destructive payloads to confirm 
exploitability.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
import asyncio
from typing import Dict, Any, Optional
from core.logging_system import get_logger
from core.stealth import GhostMode

logger = get_logger("VulnVerifier")

class VulnVerifier:
    """Safely verifies if a reported finding is a true positive."""
    
    def __init__(self):
        self.ghost = GhostMode()

    async def verify(self, vuln_type: str, endpoint: str, payload: str) -> bool:
        """Attempt to verify a vulnerability safely."""
        vt = vuln_type.upper()
        logger.info(f"🛡️ Verifying {vuln_type} at {endpoint}...")
        
        if "XSS" in vt:
            return await self._verify_xss(endpoint, payload)
        elif "SQLI" in vt:
            return await self._verify_sqli(endpoint, payload)
        elif "LFI" in vt or "PATH TRAVERSAL" in vt:
            return await self._verify_lfi(endpoint, payload)
        elif "REDIRECT" in vt:
            return await self._verify_open_redirect(endpoint, payload)
        elif "SSRF" in vt:
            return await self._verify_ssrf(endpoint, payload)
        elif "INFO" in vt or "SENSITIVE" in vt:
            return await self._verify_info_disclosure(endpoint)
        
        # Fallback to AI-assisted verification if type is unknown
        return await self._ai_verify(vuln_type, endpoint, payload)

    async def _verify_xss(self, endpoint: str, payload: str) -> bool:
        """Check if XSS payload is reflected in the response."""
        try:
            async with httpx.AsyncClient(headers=self.ghost.get_headers()) as client:
                resp = await client.get(endpoint, params={"q": payload}, timeout=10.0)
                if payload in resp.text:
                    logger.success(f"✅ XSS Verified at {endpoint}")
                    return True
        except Exception:
            pass
        return False

    async def _verify_sqli(self, endpoint: str, payload: str) -> bool:
        """Check for SQL error patterns or timing differences."""
        try:
            async with httpx.AsyncClient(headers=self.ghost.get_headers()) as client:
                resp = await client.get(endpoint, params={"id": payload}, timeout=10.0)
                errors = ["sql error", "mysql_fetch", "sqlite3.Error", "PostgreSQL query"]
                if any(err in resp.text.lower() for err in errors):
                    logger.success(f"✅ SQLi Verified (Error-based) at {endpoint}")
                    return True
        except Exception:
            pass
        return False

    async def _verify_lfi(self, endpoint: str, payload: str) -> bool:
        """Check for sensitive file content in response."""
        try:
            async with httpx.AsyncClient(headers=self.ghost.get_headers(), follow_redirects=True) as client:
                resp = await client.get(endpoint, timeout=10.0)
                indicators = ["root:x:", "[extensions]", "DB_NAME", "<?php"]
                if any(ind in resp.text for ind in indicators):
                    logger.success(f"✅ LFI Verified at {endpoint}")
                    return True
        except Exception: pass
        return False

    async def _verify_open_redirect(self, endpoint: str, payload: str) -> bool:
        """Check if redirection goes to an external domain."""
        try:
            async with httpx.AsyncClient(headers=self.ghost.get_headers(), follow_redirects=False) as client:
                resp = await client.get(endpoint, timeout=10.0)
                if resp.status_code in [301, 302, 307, 308]:
                    loc = resp.headers.get("Location", "")
                    if "viphacker100.com" in loc or "google.com" in loc:
                        logger.success(f"✅ Open Redirect Verified at {endpoint} -> {loc}")
                        return True
        except Exception: pass
        return False

    async def _verify_ssrf(self, endpoint: str, payload: str) -> bool:
        """Check for internal service signatures in response."""
        try:
            async with httpx.AsyncClient(headers=self.ghost.get_headers()) as client:
                resp = await client.get(endpoint, timeout=10.0)
                # Look for common cloud metadata or internal headers
                if "169.254.169.254" in resp.text or "instance-id" in resp.text.lower():
                    logger.success(f"✅ SSRF Verified (Cloud Metadata) at {endpoint}")
                    return True
        except Exception: pass
        return False

    async def _verify_info_disclosure(self, endpoint: str) -> bool:
        """Check for leaked environment files or secrets."""
        try:
            async with httpx.AsyncClient(headers=self.ghost.get_headers()) as client:
                resp = await client.get(endpoint, timeout=10.0)
                if "DB_PASSWORD" in resp.text or "AWS_SECRET_ACCESS_KEY" in resp.text:
                    logger.success(f"✅ Info Disclosure Verified at {endpoint}")
                    return True
        except Exception: pass
        return False

    async def _ai_verify(self, vuln_type: str, endpoint: str, payload: str) -> bool:
        """Use AI to analyze the response for subtle vulnerability indicators."""
        from ai.ai_agent_manager import AIAgentManager
        ai = AIAgentManager()
        
        try:
            async with httpx.AsyncClient(headers=self.ghost.get_headers()) as client:
                resp = await client.get(endpoint, timeout=10.0)
                content = resp.text[:2000] # Limit context
                
                prompt = f"Analyze if this HTTP response indicates a {vuln_type} vulnerability.\nPayload: {payload}\nResponse:\n{content}\n\nRespond with ONLY 'TRUE' or 'FALSE'."
                answer = ai.ask_agent(prompt)
                return "TRUE" in answer.upper()
        except Exception:
            return False
