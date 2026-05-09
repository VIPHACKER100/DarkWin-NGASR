"""DARKWIN API Integration Utilities

Provides common patterns for API integrations: rate limiting,
error handling, timeout management, and request logging.

Exports:
    RateLimiter: Track and enforce API rate limits
    APIError: Custom exception for API errors
    parse_rate_limit_headers(): Extract limits from responses
    
Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from core.logging_system import get_logger

logger = get_logger("API.Utils")


class APIError(Exception):
    """Custom exception for API-related errors.
    
    Attributes:
        status_code: HTTP status code (if applicable)
        message: Error message
        retry_after: Seconds to wait before retry (for rate limits)
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(message)


class RateLimiter:
    """Track and enforce API rate limits with exponential backoff.
    
    Monitors rate limit headers, tracks requests, and implements
    exponential backoff strategy for rate limit compliance.
    
    Attributes:
        api_name: Name of API (for logging)
        max_requests: Max requests per window
        window_seconds: Time window for rate limit
        current_requests: Count of requests in current window
    """
    
    def __init__(
        self,
        api_name: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> None:
        """Initialize rate limiter.
        
        Args:
            api_name: Name of API for logging
            max_requests: Max requests per window (default: 100)
            window_seconds: Window duration in seconds (default: 60)
        """
        self.api_name = api_name
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []  # List of request timestamps
        self.retry_count = 0
        self.max_retries = 3
    
    def check_rate_limit(self) -> bool:
        """Check if we can make a request.
        
        Returns:
            True if request can proceed, False if rate limited
        """
        now = time.time()
        
        # Remove old requests outside current window
        self.requests = [
            req_time for req_time in self.requests
            if now - req_time < self.window_seconds
        ]
        
        # Check if at limit
        if len(self.requests) >= self.max_requests:
            return False
        
        return True
    
    def record_request(self) -> None:
        """Record a request timestamp."""
        self.requests.append(time.time())
    
    def handle_rate_limit(self, retry_after: Optional[int] = None) -> float:
        """Calculate backoff time for rate limit.
        
        Args:
            retry_after: Server-provided retry-after value (seconds)
            
        Returns:
            Seconds to wait before retrying
        """
        if retry_after:
            wait_time = retry_after
        else:
            # Exponential backoff: 2, 4, 8 seconds
            wait_time = min(2 ** self.retry_count, 300)  # Cap at 5 min
        
        self.retry_count += 1
        
        logger.warning(
            f"{self.api_name} rate limited. Waiting {wait_time}s "
            f"(retry {self.retry_count}/{self.max_retries})"
        )
        
        return wait_time
    
    def reset(self) -> None:
        """Reset rate limiter (after successful request)."""
        self.retry_count = 0
    
    def should_retry(self) -> bool:
        """Check if we should retry after rate limit.
        
        Returns:
            True if under max retries, False otherwise
        """
        return self.retry_count < self.max_retries


def parse_rate_limit_headers(response_headers: Dict[str, Any]) -> Optional[int]:
    """Extract retry-after value from response headers.
    
    Checks common rate limit headers used by various APIs.
    
    Args:
        response_headers: HTTP response headers
        
    Returns:
        Seconds to wait, or None if not found
    """
    # Common header names for rate limit info
    retry_headers = [
        "Retry-After",
        "retry-after",
        "X-Rate-Limit-Reset",
        "x-ratelimit-reset",
    ]
    
    for header_name in retry_headers:
        if header_name in response_headers:
            try:
                # Try to parse as seconds
                value = response_headers[header_name]
                return int(value)
            except (ValueError, TypeError):
                logger.warning(
                    f"Could not parse {header_name}: {value}"
                )
                continue
    
    return None


def validate_api_key(api_key: Optional[str], api_name: str) -> str:
    """Validate API key exists and has minimum length.
    
    Args:
        api_key: API key to validate
        api_name: Name of API (for logging)
        
    Returns:
        The api_key if valid
        
    Raises:
        APIError: If key is invalid
    """
    if not api_key:
        raise APIError(
            f"{api_name} API key not configured",
            status_code=401
        )
    
    if len(api_key) < 5:
        raise APIError(
            f"{api_name} API key appears invalid (too short)",
            status_code=401
        )
    
    logger.debug(f"{api_name} API key validated")
    return api_key