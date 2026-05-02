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
        try:
            self.redis = redis.from_url(config.redis.url)
            logger.info("Cache Manager initialized (Redis)")
        except Exception as e:
            logger.error(f"Failed to connect to Redis for caching: {e}")
            self.redis = None

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if not self.redis: return None
        
        try:
            data = self.redis.get(f"darkwin:cache:{key}")
            if data:
                return json.loads(data)
        except Exception as e:
            logger.debug(f"Cache get error for {key}: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Store value in cache with TTL (default 1 hour)."""
        if not self.redis: return
        
        try:
            self.redis.setex(
                f"darkwin:cache:{key}",
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.debug(f"Cache set error for {key}: {e}")

    def delete(self, key: str):
        """Invalidate a specific cache key."""
        if self.redis:
            self.redis.delete(f"darkwin:cache:{key}")

# Singleton instance
global_cache = CacheManager()
