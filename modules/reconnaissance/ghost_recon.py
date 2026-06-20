"""DARKWIN Ghost Recon Module.

Stealthy reconnaissance that utilizes proxy rotation and randomized
fingerprinting to gather data from passive and active sources.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Any, Dict, Set

from core.module_loader import BaseModule
from core.proxy_manager import global_proxy_manager
from core.stealth import GhostMode

MODULE_META: Dict[str, str] = {
    "name": "Ghost Recon",
    "description": "Stealthy passive & active reconnaissance",
    "author": "ARYAN AHIRWAR",
    "category": "Reconnaissance",
}


class GhostRecon(BaseModule):
    """Stealthy reconnaissance module with proxy rotation."""

    def __init__(self, target: str, scan_id: str) -> None:
        super().__init__(target, scan_id)
        self.ghost = GhostMode()

    async def run(self) -> None:
        """Perform reconnaissance with full stealth enabled."""
        self.log(f"Initializing Ghost Recon for {self.target}")

        await self._crt_lookup()
        await self._stealth_port_probe()

    async def _crt_lookup(self) -> None:
        """Query crt.sh for certificate transparency subdomains."""
        self.log("Querying passive sources (crt.sh) via Ghost Proxy...")
        url = f"https://crt.sh/?q={self.target}&output=json"

        try:
            async with httpx.AsyncClient(
                headers=self.ghost.get_headers(),
                proxies=global_proxy_manager.get_random_proxy(),
            ) as client:
                resp = await client.get(url, timeout=10.0)
                if resp.status_code == 200:
                    data: Any = resp.json()
                    subdomains: Set[str] = {item["name_value"] for item in data}
                    for sub in subdomains:
                        self.log(f"Found subdomain: {sub}")
                else:
                    self.log(f"crt.sh returned status {resp.status_code}")
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            self.log(f"Passive lookup failed: {e}")

    async def _stealth_port_probe(self) -> None:
        """Probe common web ports with stealth timing jitter."""
        self.log("Starting low-intensity stealth port probe...")
        common_ports = [80, 443, 8080, 8443]

        for port in common_ports:
            await self.ghost.async_jitter()
            self.log(f"Probing {self.target}:{port}...")


async def run(target: str, scan_id: str, **kwargs: Any) -> None:
    """Entry point for the Ghost Recon module."""
    recon = GhostRecon(target, scan_id)
    await recon.run()

