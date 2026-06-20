"""DARKWIN Global Distributed Rate Limiter

Uses Redis to enforce rate limits across multiple scanning nodes
to prevent target overload and WAF triggering.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

"""
DARKWIN Global Distributed Rate Limiter

Uses Redis to enforce rate limits across multiple scanning nodes
to prevent target overload and WAF triggering.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: MIT
"""

import time
from typing import Optional
import redis
from redis.exceptions import RedisError
from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("RateLimiter")
config = get_config()


class RateLimiter:
    """Global rate limiter using Redis with local fallback."""

    def __init__(self) -> None:
        self.redis: Optional[redis.Redis] = None
        try:
            self.redis = redis.from_url(config.redis.url)
            logger.debug("Rate limiter connected to Redis")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis for rate limiting: {e}")

    def is_allowed(self, key: str, limit: int, period: int = 60) -> bool:
        """Check if action is allowed under rate limit.

        Args:
            key: Unique key (e.g., target domain or IP).
            limit: Maximum allowed actions per period.
            period: Time window in seconds (default: 60).

        Returns:
            True if allowed, False if limit exceeded.
        """
        if not self.redis:
            return True

        redis_key = f"rate_limit:{key}"
        try:
            current = self.redis.get(redis_key)
            if current is not None and int(current) >= limit:
                return False

            pipe = self.redis.pipeline()
            pipe.incr(redis_key)
            pipe.expire(redis_key, period)
            pipe.execute()
            return True
        except RedisError as e:
            logger.error(f"Rate limiting error: {e}")
            return True

    def wait_if_needed(self, key: str, limit: int, period: int = 60, retry_delay: float = 1.0) -> None:
        """Block until rate limit allows the action.

        Args:
            key: Unique key (e.g., target domain or IP).
            limit: Maximum allowed actions per period.
            period: Time window in seconds (default: 60).
            retry_delay: Seconds to wait between retries (default: 1.0).
        """
        while not self.is_allowed(key, limit, period):
            logger.warning(f"Rate limit reached for {key}. Waiting {retry_delay}s...")
            time.sleep(retry_delay)


global_limiter: RateLimiter = RateLimiter()
