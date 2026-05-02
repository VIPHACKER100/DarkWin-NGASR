"""DARKWIN Proxy Rotation & Management

Handles rotation of HTTP/SOCKS proxies to avoid IP-based blocking
and improve scan anonymity.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import random
from typing import List, Dict, Optional
from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("ProxyManager")
config = get_config()

class ProxyManager:
    """Manages a pool of proxies for scanning modules."""
    
    def __init__(self, proxy_file: Optional[str] = None):
        self.proxies: List[str] = []
        self.proxy_file = proxy_file or config.get("proxy_file")
        
        if self.proxy_file:
            self._load_proxies()
        else:
            # Check if proxies are in config directly
            self.proxies = config.get("proxies", [])

    def _load_proxies(self):
        """Load proxies from file (format: ip:port or user:pass@ip:port)."""
        try:
            with open(self.proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(self.proxies)} proxies from {self.proxy_file}")
        except Exception as e:
            logger.error(f"Failed to load proxies from {self.proxy_file}: {e}")

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Return a random proxy in requests/httpx format."""
        if not self.proxies:
            return None
            
        proxy = random.choice(self.proxies)
        # Assuming HTTP for now, could be expanded to SOCKS
        return {
            "http://": f"http://{proxy}",
            "https://": f"http://{proxy}"
        }

    def get_proxy_list(self) -> List[str]:
        return self.proxies

# Singleton instance
global_proxy_manager = ProxyManager()
