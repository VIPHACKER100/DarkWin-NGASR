"""
DARKWIN Censys Integration Module with Security Hardening

Provides rate-limited, error-handled access to the Censys search API
for use within scan pipelines. Validates API credentials and enforces
structured error handling.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: MIT
"""

import httpx
from typing import List, Dict, Any
from integrations.api_utils import APIError, RateLimiter, validate_api_key
from core.logging_system import get_logger

logger = get_logger("Censys.Integration")
rate_limiter = RateLimiter(api_name="Censys", max_requests=25, window_seconds=60)

def run_censys_search(query: str, config: Dict) -> List[Dict[str, Any]]:
    """
    Searches Censys for hosts matching the given query.

    Args:
        query: Censys search query string.
        config: Application configuration dict with api_keys section.

    Returns:
        List of host hit dicts from the Censys API.

    Raises:
        APIError: On rate limit, HTTP errors, or network failures.
    """
    api_id = validate_api_key(config.get("api_keys", {}).get("censys_id", ""), "Censys")
    api_secret = validate_api_key(config.get("api_keys", {}).get("censys_secret", ""), "Censys")

    url = "https://search.censys.io/api/v2/hosts/search"
    params = {"q": query}

    if not rate_limiter.check_rate_limit():
        wait_time = rate_limiter.handle_rate_limit()
        logger.warning(f"Rate limit hit. Waiting {wait_time}s before retrying.")
        raise APIError("Censys rate limit exceeded. Please try again later.")

    try:
        with httpx.Client(auth=(api_id, api_secret), timeout=10.0) as client:
            response = client.get(url, params=params)
            rate_limiter.record_request()
            if response.status_code == 200:
                logger.info(f"Censys search successful for query: {query}")
                return response.json().get("result", {}).get("hits", [])
            else:
                logger.error(f"Censys API Error: {response.status_code} {response.text}")
                raise APIError(f"Censys API Error: {response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Censys request error: {e}")
        raise APIError(f"Censys request error: {e}")
    except APIError as e:
        raise
    except (ValueError, json.JSONDecodeError, KeyError) as e:
        logger.critical(f"Unexpected error in Censys integration: {e}")
        raise APIError(f"Unexpected error in Censys integration: {e}")
