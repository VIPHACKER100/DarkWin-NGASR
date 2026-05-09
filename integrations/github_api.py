"""DARKWIN GitHub API Integration with Security Hardening

Provides secure GitHub code search with rate limiting and error handling.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Dict, List, Optional
from urllib.parse import quote
from core.config_manager import get_config
from core.logging_system import get_logger
from integrations.api_utils import RateLimiter, APIError, validate_api_key, parse_rate_limit_headers

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

    def search_code(self, query: str, pages: int = 1) -> Dict[str, any]:
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

            all_items = []
            total_count = 0
            
            # per_page max is 100 for GitHub
            results_per_page = 30 
            
            # URL encode query for safety
            encoded_query = quote(query.strip())
            
            with httpx.Client(timeout=DEFAULT_TIMEOUT, verify=True) as client:
                for page in range(1, pages + 1):
                    url = f"{GITHUB_BASE_URL}/search/code?q={encoded_query}&per_page={results_per_page}&page={page}"

                    # Check rate limit before each page request
                    if not self.limiter.check_rate_limit():
                        wait_time = self.limiter.handle_rate_limit()
                        logger.warning(f"Rate limited during pagination, waiting {wait_time}s")
                        break # Stop and return what we have

                    # Record the request
                    self.limiter.record_request()

                    response = client.get(url, headers=self.headers)

                    # Handle rate limiting
                    if response.status_code == 403:
                        rate_limit_info = parse_rate_limit_headers(response.headers)
                        logger.warning("GitHub secondary rate limit hit. Returning partial results.")
                        break

                    if response.status_code != 200:
                        logger.error(f"GitHub API Error on page {page}: {response.status_code}")
                        break

                    data = response.json()
                    total_count = data.get("total_count", 0)
                    
                    items = data.get("items", [])
                    if not items:
                        break # No more results
                        
                    for item in items:
                        try:
                            repo_info = item.get("repository", {})
                            all_items.append({
                                "repository": repo_info.get("full_name", "unknown"),
                                "html_url": item.get("html_url", ""),
                                "path": item.get("path", ""),
                                "score": item.get("score", 0)
                            })
                        except (KeyError, TypeError) as e:
                            continue
                    
                    # If we have reached total_count, stop
                    if len(all_items) >= total_count:
                        break

            result = {
                "total_count": total_count,
                "items": all_items
            }

            logger.info(f"GitHub code search successful: {len(all_items)} results for query '{query}'")
            return result


        except httpx.TimeoutException as e:
            logger.error(f"GitHub request timeout for query '{query}': {e}")
            return {"error": "Request timeout"}
        except httpx.RequestError as e:
            logger.error(f"GitHub request error for query '{query}': {e}")
            return {"error": "Network request failed"}
        except ValueError as e:
            logger.error(f"Invalid JSON response from GitHub: {e}")
            return {"error": "Invalid response format"}
        except Exception as e:
            error_msg = f"Unexpected error searching GitHub: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg}


# Legacy function for backward compatibility
def search_code(query: str) -> Dict[str, any]:
    """Legacy function - use GitHubAPI class instead."""
    try:
        api = GitHubAPI()
        return api.search_code(query)
    except Exception as e:
        logger.error(f"Legacy search_code failed: {e}")
        return {"error": str(e)}
