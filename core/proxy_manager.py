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
        # Handle cases where proxy string already has protocol
        if "://" not in proxy:
            proxy = f"http://{proxy}"
            
        return {
            "http://": proxy,
            "https://": proxy
        }

    async def validate_proxy(self, proxy_url: str) -> bool:
        """Test if a proxy is responding and not leaking real IP.
        
        Args:
            proxy_url: The proxy URL to test.
            
        Returns:
            True if proxy is healthy, False otherwise.
        """
        import httpx
        try:
            # Protocol must be specified for httpx
            test_proxy = proxy_url if "://" in proxy_url else f"http://{proxy_url}"
            proxies = {"all://": test_proxy}
            
            async with httpx.AsyncClient(proxies=proxies, timeout=5.0) as client:
                # Use a reliable target for health checks
                resp = await client.get("https://httpbin.org/ip")
                if resp.status_code == 200:
                    origin = resp.json().get("origin", "")
                    logger.debug(f"Proxy {test_proxy} validated successfully. Origin: {origin}")
                    return True
        except Exception as e:
            logger.debug(f"Proxy validation failed for {proxy_url}: {e}")
        
        return False

    async def cleanup_dead_proxies(self):
        """Iterate through the proxy pool and remove unresponsive entries."""
        if not self.proxies:
            return

        logger.info(f"🔄 Starting cleanup of dead proxies ({len(self.proxies)} in pool)")
        valid_proxies = []
        
        # Check in batches to avoid overwhelming
        import asyncio
        batch_size = 10
        for i in range(0, len(self.proxies), batch_size):
            batch = self.proxies[i:i+batch_size]
            tasks = [self.validate_proxy(p) for p in batch]
            results = await asyncio.gather(*tasks)
            
            for proxy, is_valid in zip(batch, results):
                if is_valid:
                    valid_proxies.append(proxy)
        
        removed_count = len(self.proxies) - len(valid_proxies)
        self.proxies = valid_proxies
        
        if removed_count > 0:
            logger.info(f"✨ Purged {removed_count} dead proxies. {len(self.proxies)} remaining.")
        else:
            logger.info("✅ All proxies in pool are healthy.")

    def get_proxy_list(self) -> List[str]:
        return self.proxies

# Singleton instance
global_proxy_manager = ProxyManager()

