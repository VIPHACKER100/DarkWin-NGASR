"""DARKWIN Shodan API Integration with Security Hardening

Provides secure Shodan API queries with rate limiting and timeout handling.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import shodan
from typing import Dict, Optional
from core.config_manager import get_config
from core.logging_system import get_logger
from integrations.api_utils import RateLimiter, APIError, validate_api_key

logger = get_logger("Integrations.Shodan")
config = get_config()

# Constants
DEFAULT_TIMEOUT: int = 10  # Shodan recommends 10s timeout


class ShodanAPI:
    """Secure Shodan API client with rate limiting and error handling."""

    def __init__(self) -> None:
        """Initialize Shodan API client with security hardening."""
        self.api_key = config.integrations.get('shodan_api_key')
        if not self.api_key:
            logger.error("Shodan API key not configured")
            raise ValueError("SHODAN_API_KEY not configured in config.yaml")

        try:
            validate_api_key(self.api_key, "Shodan")
        except ValueError as e:
            logger.error(f"Invalid Shodan API key: {e}")
            raise

        # Initialize rate limiter (Shodan free tier: 1 request/second)
        self.limiter = RateLimiter("Shodan", max_requests=1, window_seconds=1)

        # Initialize Shodan client with timeout
        try:
            self.api = shodan.Shodan(self.api_key)
            # Note: Shodan client doesn't directly support timeout in constructor
            # We'll handle timeout in individual calls
            logger.info("Shodan API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Shodan client: {e}")
            raise

    def search_host(self, ip: str) -> Dict[str, any]:
        """Query Shodan for information about a specific IP address.

        Implements rate limiting, timeout handling, and secure error management.

        Args:
            ip: IP address to search for

        Returns:
            Dictionary containing host information, or error dict if failed
        """
        try:
            # Validate IP format (basic check)
            if not self._validate_ip(ip):
                logger.error(f"Invalid IP address format: {ip}")
                return {"error": "Invalid IP address format"}

            # Check rate limit
            if not self.limiter.check_rate_limit():
                wait_time = self.limiter.handle_rate_limit()
                logger.warning(f"Rate limited, waiting {wait_time}s")
                return {"error": f"Rate limited. Try again in {wait_time} seconds"}

            # Record the request
            self.limiter.record_request()

            # Make API call with timeout handling
            # Note: shodan-python doesn't have built-in timeout, so we use a wrapper
            host_data = self._api_call_with_timeout(
                lambda: self.api.host(ip),
                timeout=DEFAULT_TIMEOUT
            )

            # Process and sanitize response
            result = {
                "ip": host_data.get('ip_str', ip),
                "organization": host_data.get('org', 'n/a'),
                "os": host_data.get('os', 'n/a'),
                "ports": host_data.get('ports', []),
                "hostnames": host_data.get('hostnames', []),
                "vulns": host_data.get('vulns', []),
                "last_update": host_data.get('last_update'),
                "country": host_data.get('country_name', 'n/a')
            }

            logger.info(f"Successfully queried Shodan for IP: {ip}")
            return result

        except shodan.APIError as e:
            error_msg = f"Shodan API Error: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
        except APIError as e:
            logger.error(f"API Error: {e.message}")
            return {"error": e.message}
        except Exception as e:
            error_msg = f"Unexpected error querying Shodan: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg}

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
        """Execute API call with timeout handling."""
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"API call timed out after {timeout} seconds")

        # Set up timeout signal
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        try:
            result = api_call()
            return result
        finally:
            # Restore original handler and cancel alarm
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


# Legacy function for backward compatibility
def search_host(ip: str) -> Dict[str, any]:
    """Legacy function - use ShodanAPI class instead."""
    try:
        api = ShodanAPI()
        return api.search_host(ip)
    except Exception as e:
        logger.error(f"Legacy search_host failed: {e}")
        return {"error": str(e)}
