"""DARKWIN AI-Powered Vulnerability Fuzzer

Uses LLM to generate context-aware payloads based on the specific
technology stack and endpoint parameters detected.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Any, Dict, List

import httpx

from ai.ai_agent_manager import AIAgentManager
from core.module_loader import BaseModule
from core.proxy_manager import global_proxy_manager
from core.stealth import GhostMode

MODULE_META: Dict[str, str] = {
    "name": "AI Fuzzer",
    "description": "Smart payload generation using LLM",
    "author": "ARYAN AHIRWAR",
    "category": "Web Scanning",
    "vulnerability_types": ["XSS", "SQLi", "SSRF", "RCE"],
}


class AIFuzzer(BaseModule):
    """Next-gen fuzzer that uses AI for payload generation."""

    def __init__(self, target: str, scan_id: str) -> None:
        super().__init__(target, scan_id)
        self.ai = AIAgentManager()
        self.ghost = GhostMode()

    async def run(self, endpoint: str, params: Dict[str, Any], tech_stack: List[str]) -> None:
        """Analyze endpoint and tech stack to generate and test payloads."""
        self.log(f"AI Analyzing endpoint: {endpoint} (Tech: {tech_stack})")

        prompt = (
            f"Generate 3 highly specialized security testing payloads for the following:\n"
            f"Endpoint: {endpoint}\n"
            f"Parameters: {params}\n"
            f"Technology Stack: {tech_stack}\n\n"
            f"Target Vulnerability: Injection & SSRF.\n"
            f"Format: Return only a comma-separated list of payloads."
        )

        try:
            response = await self.ai.async_ask_agent(prompt)
            payloads = [p.strip() for p in response.split(",")]
        except (AttributeError, ValueError, TypeError) as e:
            self.log(f"AI Payload Generation failed: {e}")
            return

        proxies = global_proxy_manager.get_random_proxy()
        proxy_url = None
        if proxies:
            proxy_url = {"all://": list(proxies.values())[0]}

        async with httpx.AsyncClient(
            headers=self.ghost.get_headers(), proxies=proxy_url
        ) as client:
            for payload in payloads:
                self.log(f"Testing Payload: {payload}")
                for param in params:
                    try:
                        test_params = params.copy()
                        test_params[param] = payload
                        resp = await client.get(endpoint, params=test_params, timeout=5.0)
                        if self._is_vulnerable(resp, payload):
                            self.add_finding(
                                vuln_type="AI Detected Vulnerability",
                                severity="Critical",
                                endpoint=endpoint,
                                description=f"Potential vulnerability found using AI-generated payload: {payload}",
                                payload=payload,
                            )
                    except (httpx.RequestError, httpx.HTTPStatusError) as e:
                        self.log(f"Request failed: {e}")

    def _is_vulnerable(self, resp: httpx.Response, payload: str) -> bool:
        """Basic heuristic for vulnerability detection."""
        if payload in resp.text:
            return True
        if "sql error" in resp.text.lower():
            return True
        if resp.status_code == 500:
            return True
        return False


async def run(target: str, scan_id: str, config: dict, **kwargs: Any) -> None:
    """Entry point for the AI Fuzzer module."""
    fuzzer = AIFuzzer(target, scan_id)
    endpoint = kwargs.get("endpoint", target)
    params = kwargs.get("params", {})
    tech_stack = kwargs.get("tech_stack", [])
    await fuzzer.run(endpoint, params, tech_stack)

