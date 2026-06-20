"""DARKWIN GitHub API Integration with Security Hardening.

Provides secure GitHub code search with rate limiting and error handling.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

from core.config_manager import get_config
from core.logging_system import get_logger
from integrations.api_utils import APIError, RateLimiter, parse_rate_limit_headers, validate_api_key

logger = get_logger("Integrations.GitHub")
config = get_config()

# Constants
DEFAULT_TIMEOUT: int = 15  # GitHub can be slower for code search
GITHUB_BASE_URL: str = "https://api.github.com"
MAX_RESULTS: int = 5


class GitHubAPI:
    """Secure GitHub API client with rate limiting and error handling."""

    def __init__(self) -> None:
        """Initialize GitHub API client with security hardening."""
        self.token = config.integrations.get('github_token')
        if not self.token:
            logger.error("GitHub token not configured")
            raise ValueError("GITHUB_TOKEN not configured in config.yaml")

        try:
            validate_api_key(self.token, "GitHub")
        except ValueError as e:
            logger.error(f"Invalid GitHub token: {e}")
            raise

        # Initialize rate limiter (GitHub: 30 requests/minute for search)
        self.limiter = RateLimiter("GitHub", max_requests=30, window_seconds=60)

        # Common headers
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}",
            "User-Agent": "DARKWIN-Security-Scanner/1.0"
        }

        logger.info("GitHub API client initialized successfully")

    def search_code(self, query: str, pages: int = 1) -> Dict[str, Any]:
        """Search GitHub for code with security hardening and pagination support.

        Args:
            query: Search query string
            pages: Number of pages to fetch (max 100 results per page)

        Returns:
            Search results dictionary, or error dict if failed
        """
        try:
            if not query or not query.strip():
                logger.error("Empty or invalid search query")
                return {"error": "Invalid search query"}

            all_items: List[Dict[str, Any]] = []
            total_count = 0
            results_per_page = 30
            encoded_query = quote(query.strip())

            with httpx.Client(timeout=DEFAULT_TIMEOUT, verify=True) as client:
                for page in range(1, pages + 1):
                    url = f"{GITHUB_BASE_URL}/search/code?q={encoded_query}&per_page={results_per_page}&page={page}"

                    if not self.limiter.check_rate_limit():
                        wait_time = self.limiter.handle_rate_limit()
                        logger.warning(f"Rate limited during pagination, waiting {wait_time}s")
                        break

                    self.limiter.record_request()

                    response = client.get(url, headers=self.headers)

                    if response.status_code == 403:
                        parse_rate_limit_headers(response.headers)
                        logger.warning("GitHub secondary rate limit hit. Returning partial results.")
                        break

                    if response.status_code != 200:
                        logger.error(f"GitHub API Error on page {page}: {response.status_code}")
                        break

                    data = response.json()
                    total_count = data.get("total_count", 0)
                    items = data.get("items", [])

                    if not items:
                        break

                    for item in items:
                        try:
                            repo_info = item.get("repository", {})
                            all_items.append({
                                "repository": repo_info.get("full_name", "unknown"),
                                "html_url": item.get("html_url", ""),
                                "path": item.get("path", ""),
                                "score": item.get("score", 0),
                            })
                        except (KeyError, TypeError):
                            continue

                    if len(all_items) >= total_count:
                        break

            result = {"total_count": total_count, "items": all_items}
            logger.info(f"GitHub code search successful: {len(all_items)} results for query '{query}'")
            return result

        except httpx.TimeoutException as e:
            logger.error(f"GitHub request timeout for query '{query}': {e}")
            return {"error": "Request timeout"}
        except httpx.RequestError as e:
            logger.error(f"GitHub request error for query '{query}': {e}")
            return {"error": "Network request failed"}
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Invalid response from GitHub: {e}")
            return {"error": "Invalid response format"}


# Legacy function for backward compatibility
def search_code(query: str) -> Dict[str, Any]:
    """Legacy function - use GitHubAPI class instead."""
    try:
        api = GitHubAPI()
        return api.search_code(query)
    except (ValueError, httpx.RequestError) as e:
        logger.error(f"Legacy search_code failed: {e}")
        return {"error": str(e)}
