import httpx
from typing import Dict, Any
from integrations.api_utils import APIError, RateLimiter, validate_api_key
from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("Censys.API")
config = get_config()
rate_limiter = RateLimiter(api_name="Censys", max_requests=25, window_seconds=60)

def search_host(ip: str) -> Dict[str, Any]:
    """
    Queries Censys for information about a specific IP address with error handling and rate limiting.
    """
    api_id = validate_api_key(config.integrations.get('censys_api_id'), "Censys")
    api_secret = validate_api_key(config.integrations.get('censys_api_secret'), "Censys")

    url = f"https://search.censys.io/api/v2/hosts/{ip}"
    if not rate_limiter.check_rate_limit():
        wait_time = rate_limiter.handle_rate_limit()
        logger.warning(f"Rate limit hit. Waiting {wait_time}s before retrying.")
        raise APIError("Censys rate limit exceeded. Please try again later.")

    try:
        with httpx.Client(timeout=10.0, auth=(api_id, api_secret)) as client:
            response = client.get(url)
            rate_limiter.record_request()
            if response.status_code == 200:
                data = response.json().get('result', {})
                services = data.get('services', [])
                ports = [s.get('port') for s in services]
                logger.info(f"Censys search successful for {ip}.")
                return {
                    "ip": ip,
                    "ports": ports,
                    "services": len(services)
                }
            else:
                logger.error(f"Censys API Error: {response.status_code} {response.text}")
                raise APIError(f"Censys API Error: {response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Censys request error: {e}")
        raise APIError(f"Censys request error: {e}")
    except APIError as e:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error in Censys search: {e}")
        raise APIError(f"Unexpected error in Censys search: {e}")
