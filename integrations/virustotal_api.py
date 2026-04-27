"""DARKWIN VirusTotal API Integration with Security Hardening

Provides secure VirusTotal domain and file analysis with rate limiting.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Dict, Optional
from urllib.parse import quote
from core.config_manager import get_config
from core.logging_system import get_logger
from integrations.api_utils import RateLimiter, APIError, validate_api_key

logger = get_logger("Integrations.VirusTotal")
config = get_config()

# Constants
DEFAULT_TIMEOUT: int = 15  # VirusTotal can be slower
VT_BASE_URL: str = "https://www.virustotal.com/api/v3"


class VirusTotalAPI:
    """Secure VirusTotal API client with rate limiting and error handling."""

    def __init__(self) -> None:
        """Initialize VirusTotal API client with security hardening."""
        self.api_key = config.integrations.get('vt_api_key')
        if not self.api_key:
            logger.error("VirusTotal API key not configured")
            raise ValueError("VT_API_KEY not configured in config.yaml")

        try:
            validate_api_key(self.api_key, "VirusTotal")
        except ValueError as e:
            logger.error(f"Invalid VirusTotal API key: {e}")
            raise

        # Initialize rate limiter (VirusTotal free tier: ~4 requests/minute)
        self.limiter = RateLimiter("VirusTotal", max_requests=4, window_seconds=60)

        # Common headers
        self.headers = {
            "x-apikey": self.api_key,
            "Accept": "application/json"
        }

        logger.info("VirusTotal API client initialized successfully")

    def get_domain_report(self, domain: str) -> Dict[str, any]:
        """Query VirusTotal for a domain report with security hardening.

        Args:
            domain: Domain name to analyze

        Returns:
            Domain analysis results, or error dict if failed
        """
        try:
            # Validate domain
            if not self._validate_domain(domain):
                logger.error(f"Invalid domain format: {domain}")
                return {"error": "Invalid domain format"}

            # Check rate limit
            if not self.limiter.check_rate_limit():
                wait_time = self.limiter.handle_rate_limit()
                logger.warning(f"Rate limited, waiting {wait_time}s")
                return {"error": f"Rate limited. Try again in {wait_time} seconds"}

            # Record the request
            self.limiter.record_request()

            # URL encode domain for safety
            encoded_domain = quote(domain)
            url = f"{VT_BASE_URL}/domains/{encoded_domain}"

            # Make request with timeout and SSL verification
            with httpx.Client(timeout=DEFAULT_TIMEOUT, verify=True) as client:
                response = client.get(url, headers=self.headers)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    logger.warning(f"VirusTotal rate limit exceeded, retry after {retry_after}s")
                    return {"error": f"Rate limited. Try again in {retry_after} seconds"}

                if response.status_code == 200:
                    data = response.json()
                    attributes = data.get('data', {}).get('attributes', {})

                    result = {
                        "domain": domain,
                        "reputation": attributes.get('reputation', 0),
                        "last_analysis_stats": attributes.get('last_analysis_stats', {}),
                        "last_analysis_date": attributes.get('last_analysis_date'),
                        "categories": attributes.get('categories', {}),
                        "total_votes": attributes.get('total_votes', {})
                    }

                    logger.info(f"Successfully retrieved VirusTotal report for domain: {domain}")
                    return result

                elif response.status_code == 404:
                    logger.info(f"Domain not found in VirusTotal: {domain}")
                    return {"error": "Domain not found in VirusTotal database"}
                else:
                    error_msg = f"VirusTotal API Error: {response.status_code}"
                    logger.error(error_msg)
                    return {"error": error_msg}

        except httpx.TimeoutException as e:
            logger.error(f"VirusTotal request timeout for domain {domain}: {e}")
            return {"error": "Request timeout"}
        except httpx.RequestError as e:
            logger.error(f"VirusTotal request error for domain {domain}: {e}")
            return {"error": "Network request failed"}
        except ValueError as e:
            logger.error(f"Invalid JSON response from VirusTotal: {e}")
            return {"error": "Invalid response format"}
        except Exception as e:
            error_msg = f"Unexpected error querying VirusTotal: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg}

    def _validate_domain(self, domain: str) -> bool:
        """Basic domain name validation."""
        if not domain or len(domain) > 253:
            return False

        # Simple regex for domain validation
        import re
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        )
        return bool(domain_pattern.match(domain))


# Legacy function for backward compatibility
def get_domain_report(domain: str) -> Dict[str, any]:
    """Legacy function - use VirusTotalAPI class instead."""
    try:
        api = VirusTotalAPI()
        return api.get_domain_report(domain)
    except Exception as e:
        logger.error(f"Legacy get_domain_report failed: {e}")
        return {"error": str(e)}
