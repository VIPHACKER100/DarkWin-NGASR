"""
DARKWIN Caching Manager

Provides an interface for storing and retrieving ephemeral scan results
to speed up repeated lookups and minimize redundant network traffic.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: MIT
"""

import json
import time
from typing import Any, Optional, Dict, Tuple

from redis import Redis
from redis.exceptions import RedisError
from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("CacheManager")
config = get_config()


class CacheManager:
    """Interface for Redis-backed caching with in-memory fallback."""

    def __init__(self) -> None:
        self.local_cache: Dict[str, Tuple[Any, float]] = {}
        self.redis: Optional[Redis] = None
        try:
            self.redis = Redis.from_url(config.redis.url)
            self.redis.ping()
            logger.info("Cache Manager initialized (Redis)")
        except RedisError as e:
            logger.warning(f"Redis unavailable, falling back to in-memory caching: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache.

        Args:
            key: Cache key to look up.

        Returns:
            Cached value or None if not found or expired.
        """
        if self.redis:
            try:
                data = self.redis.get(f"darkwin:cache:{key}")
                if data:
                    return json.loads(data)
            except RedisError as e:
                logger.debug(f"Redis get error for {key}: {e}")

        if key in self.local_cache:
            val, expiry = self.local_cache[key]
            if expiry > time.time():
                return val
            del self.local_cache[key]

        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Store a value in cache with a TTL.

        Args:
            key: Cache key.
            value: Value to store (must be JSON-serializable).
            ttl: Time-to-live in seconds (default 1 hour).
        """
        if self.redis:
            try:
                self.redis.setex(f"darkwin:cache:{key}", ttl, json.dumps(value))
                return
            except RedisError as e:
                logger.debug(f"Redis set error for {key}: {e}")

        self.local_cache[key] = (value, time.time() + ttl)

    def delete(self, key: str) -> None:
        """Invalidate a specific cache key from both Redis and local cache.

        Args:
            key: Cache key to delete.
        """
        if self.redis:
            try:
                self.redis.delete(f"darkwin:cache:{key}")
            except RedisError:
                pass

        self.local_cache.pop(key, None)


global_cache: CacheManager = CacheManager()
