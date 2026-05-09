"""DARKWIN Caching Manager

Provides an interface for storing and retrieving ephemeral scan results
to speed up repeated lookups and minimize redundant network traffic.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import redis
from typing import Any, Optional
from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("CacheManager")
config = get_config()

class CacheManager:
    """Interface for Redis-based ephemeral caching."""
    
    def __init__(self):
        self.local_cache = {} # In-memory fallback
        try:
            self.redis = redis.from_url(config.redis.url)
            self.redis.ping() # Verify connection
            logger.info("Cache Manager initialized (Redis)")
        except Exception as e:
            logger.warning(f"Redis unavailable, falling back to in-memory caching: {e}")
            self.redis = None

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        # Try Redis first
        if self.redis:
            try:
                data = self.redis.get(f"darkwin:cache:{key}")
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.debug(f"Redis get error for {key}: {e}")
        
        # Fallback to in-memory
        import time
        if key in self.local_cache:
            val, expiry = self.local_cache[key]
            if expiry > time.time():
                return val
            else:
                del self.local_cache[key] # Expired
        
        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Store value in cache with TTL (default 1 hour)."""
        # Try Redis
        if self.redis:
            try:
                self.redis.setex(
                    f"darkwin:cache:{key}",
                    ttl,
                    json.dumps(value)
                )
                return
            except Exception as e:
                logger.debug(f"Redis set error for {key}: {e}")
        
        # Fallback to in-memory
        import time
        self.local_cache[key] = (value, time.time() + ttl)

    def delete(self, key: str):
        """Invalidate a specific cache key."""
        if self.redis:
            try:
                self.redis.delete(f"darkwin:cache:{key}")
            except: pass
        
        if key in self.local_cache:
            del self.local_cache[key]

# Singleton instance
global_cache = CacheManager()
