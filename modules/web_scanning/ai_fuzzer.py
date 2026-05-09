"""DARKWIN AI-Powered Vulnerability Fuzzer

Uses LLM to generate context-aware payloads based on the specific 
technology stack and endpoint parameters detected.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
import asyncio
from typing import List, Dict, Any
from core.module_loader import BaseModule
from ai.ai_agent_manager import AIAgentManager
from core.stealth import GhostMode
from core.proxy_manager import global_proxy_manager

class AIFuzzer(BaseModule):
    """Next-gen fuzzer that uses AI for payload generation."""
    
    MODULE_META = {
        "name": "AI Fuzzer",
        "description": "Smart payload generation using LLM",
        "author": "ARYAN AHIRWAR",
        "category": "vulnerability",
        "vulnerability_types": ["XSS", "SQLi", "SSRF", "RCE"]
    }

    def __init__(self, target: str, scan_id: str):
        super().__init__(target, scan_id)
        self.ai = AIAgentManager()
        self.ghost = GhostMode()

    async def run(self, endpoint: str, params: Dict[str, Any], tech_stack: List[str]):
        """Analyze endpoint and tech stack to generate and test payloads."""
        self.log(f"🧠 AI Analyzing endpoint: {endpoint} (Tech: {tech_stack})")
        
        # 1. Ask AI for specialized payloads
        prompt = f"""
        Generate 3 highly specialized security testing payloads for the following:
        Endpoint: {endpoint}
        Parameters: {params}
        Technology Stack: {tech_stack}
        
        Target Vulnerability: Injection & SSRF.
        Format: Return only a comma-separated list of payloads.
        """
        
        try:
            response = await self.ai.get_reasoning(prompt)
            payloads = [p.strip() for p in response.split(",")]
        except Exception as e:
            self.log(f"❌ AI Payload Generation failed: {e}")
            return

        # 2. Execute stealthy fuzzing
        async with httpx.AsyncClient(
            headers=self.ghost.get_headers(),
            proxies=global_proxy_manager.get_random_proxy()
        ) as client:
            for payload in payloads:
                self.log(f"🚀 Testing Payload: {payload}")
                try:
                    # Test each parameter with the payload
                    for param in params:
                        test_params = params.copy()
                        test_params[param] = payload
                        
                        resp = await client.get(endpoint, params=test_params, timeout=5.0)
                        
                        # 3. Analyze response (Smart detection)
                        if self._is_vulnerable(resp, payload):
                            self.add_finding(
                                vuln_type="AI Detected Vulnerability",
                                severity="Critical",
                                endpoint=endpoint,
                                description=f"Potential vulnerability found using AI-generated payload: {payload}",
                                payload=payload
                            )
                except Exception as e:
                    self.log(f"⚠️ Request failed: {e}")

    def _is_vulnerable(self, resp: httpx.Response, payload: str) -> bool:
        """Basic heuristic for vulnerability detection."""
        # Check for reflections, database errors, or timing changes
        if payload in resp.text: return True
        if "sql error" in resp.text.lower(): return True
        if resp.status_code == 500: return True
        return False

async def run(target: str, scan_id: str, **kwargs):
    """Entry point for the AI Fuzzer module."""
    fuzzer = AIFuzzer(target, scan_id)
    # Extract extra args if provided, otherwise use defaults
    endpoint = kwargs.get("endpoint", target)
    params = kwargs.get("params", {})
    tech_stack = kwargs.get("tech_stack", [])
    
    await fuzzer.run(endpoint, params, tech_stack)

