"""DARKWIN Shodan Integration Module with Security Hardening.

Provides secure Shodan search and host lookup functionality.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import signal
from typing import Any, Dict, List, Optional

import shodan

from core.logging_system import get_logger
from integrations.api_utils import APIError, RateLimiter, validate_api_key

logger = get_logger("Integrations.ShodanIntegration")

# Constants
DEFAULT_TIMEOUT: int = 10
MAX_RESULTS: int = 100


class ShodanIntegration:
    """Secure Shodan integration with rate limiting and error handling."""

    def __init__(self, config: Dict) -> None:
        """Initialize Shodan integration with security hardening.

        Args:
            config: Configuration dictionary containing API keys
        """
        self.api_key = config.get("api_keys", {}).get("shodan", "")
        if not self.api_key:
            logger.error("Shodan API key not configured")
            raise ValueError("Shodan API key not found in config")

        try:
            validate_api_key(self.api_key, "Shodan")
        except ValueError as e:
            logger.error(f"Invalid Shodan API key: {e}")
            raise

        # Initialize rate limiter (Shodan free tier: 1 request/second)
        self.limiter = RateLimiter("Shodan", max_requests=1, window_seconds=1)

        # Initialize Shodan client
        try:
            self.api = shodan.Shodan(self.api_key)
            logger.info("Shodan integration initialized successfully")
        except (shodan.APIError, ValueError) as e:
            logger.error(f"Failed to initialize Shodan client: {e}")
            raise

    def run_shodan_search(self, query: str) -> List[Dict]:
        """Search Shodan for the given query with security hardening.

        Args:
            query: Search query string

        Returns:
            List of matching results, or empty list if failed
        """
        try:
            if not query or not query.strip():
                logger.error("Empty or invalid search query")
                return []

            # Check rate limit
            if not self.limiter.check_rate_limit():
                wait_time = self.limiter.handle_rate_limit()
                logger.warning(f"Rate limited, waiting {wait_time}s")
                return []

            # Record the request
            self.limiter.record_request()

            # Execute search with timeout handling
            results = self._api_call_with_timeout(
                lambda: self.api.search(query, limit=MAX_RESULTS),
                timeout=DEFAULT_TIMEOUT
            )

            matches = results.get("matches", [])
            logger.info(f"Shodan search successful: {len(matches)} results for query '{query}'")
            return matches

        except shodan.APIError as e:
            logger.error(f"Shodan API error during search: {e}")
            return []
        except APIError as e:
            logger.error(f"API error during search: {e.message}")
            return []
        except (ValueError, TimeoutError, KeyError) as e:
            logger.error(f"Unexpected error during Shodan search: {e}", exc_info=True)
            return []

    def get_host_info(self, ip: str) -> Dict:
        """Retrieve detailed host information from Shodan.

        Args:
            ip: IP address to query

        Returns:
            Host information dictionary, or empty dict if failed
        """
        try:
            # Validate IP format
            if not self._validate_ip(ip):
                logger.error(f"Invalid IP address format: {ip}")
                return {}

            # Check rate limit
            if not self.limiter.check_rate_limit():
                wait_time = self.limiter.handle_rate_limit()
                logger.warning(f"Rate limited, waiting {wait_time}s")
                return {}

            # Record the request
            self.limiter.record_request()

            # Get host info with timeout
            host_data = self._api_call_with_timeout(
                lambda: self.api.host(ip),
                timeout=DEFAULT_TIMEOUT
            )

            logger.info(f"Successfully retrieved host info for IP: {ip}")
            return host_data

        except shodan.APIError as e:
            logger.error(f"Shodan API error getting host info: {e}")
            return {}
        except APIError as e:
            logger.error(f"API error getting host info: {e.message}")
            return {}
        except (ValueError, TimeoutError, KeyError) as e:
            logger.error(f"Unexpected error getting host info: {e}", exc_info=True)
            return {}

    def _validate_ip(self, ip: str) -> bool:
        """Basic IP address validation."""
        if not ip:
            return False

        parts = ip.split('.')
        if len(parts) != 4:
            return False

        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False

    def _api_call_with_timeout(self, api_call, timeout: int = DEFAULT_TIMEOUT):
        """Execute API call with timeout handling (Unix signal-based)."""
        def timeout_handler(signum, frame):
            raise TimeoutError(f"API call timed out after {timeout} seconds")

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        try:
            result = api_call()
            return result
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


# Legacy functions for backward compatibility
def run_shodan_search(query: str, config: Dict) -> List[Dict]:
    """Legacy function - use ShodanIntegration class instead."""
    try:
        integration = ShodanIntegration(config)
        return integration.run_shodan_search(query)
    except (ValueError, APIError, shodan.APIError) as e:
        logger.error(f"Legacy run_shodan_search failed: {e}")
        return []


def get_host_info(ip: str, config: Dict) -> Dict:
    """Legacy function - use ShodanIntegration class instead."""
    try:
        integration = ShodanIntegration(config)
        return integration.get_host_info(ip)
    except (ValueError, APIError, shodan.APIError) as e:
        logger.error(f"Legacy get_host_info failed: {e}")
        return {}
