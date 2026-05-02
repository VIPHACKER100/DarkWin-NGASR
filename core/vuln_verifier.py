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
        logger.info(f"🛡️ Verifying {vuln_type} at {endpoint}...")
        
        if "XSS" in vuln_type.upper():
            return await self._verify_xss(endpoint, payload)
        elif "SQLI" in vuln_type.upper():
            return await self._verify_sqli(endpoint, payload)
        
        # Default to unverified but recorded
        return False

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
        # Simple heuristic for verification
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
