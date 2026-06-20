"""DARKWIN Web Crawler module.

Async BFS web crawler that discovers URLs within the target domain scope.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Dict, List, Set, Tuple

import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

MODULE_META: Dict[str, str] = {
    "name": "Web Crawler",
    "category": "Web Scanning",
    "description": "Async BFS web crawler to discover URLs within scope",
    "version": "1.0.0",
}

from typing import Dict


async def run(start_url: str, scan_id: str, config: dict, max_depth: int = 3, max_pages: int = 100) -> List[str]:
    """Async BFS web crawler that discovers URLs within the target domain.

    Args:
        start_url: The URL to begin crawling from.
        scan_id: Unique scan identifier.
        config: Application config (unused, kept for API consistency).
        max_depth: Maximum link depth to follow (default 3).
        max_pages: Maximum number of unique pages to crawl (default 100).

    Returns:
        Sorted list of discovered URLs.
    """
    discovered_urls: Set[str] = {start_url}
    queue: List[Tuple[str, int]] = [(start_url, 0)]
    domain = urlparse(start_url).netloc

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            while queue and len(discovered_urls) < max_pages:
                current_url, depth = queue.pop(0)
                if depth > max_depth:
                    continue

                try:
                    response = await client.get(current_url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        for link in soup.find_all("a", href=True):
                            absolute_url = urljoin(current_url, link["href"])
                            parsed = urlparse(absolute_url)
                            if parsed.netloc == domain:
                                clean_url = absolute_url.split("#")[0].rstrip("/")
                                if clean_url not in discovered_urls:
                                    discovered_urls.add(clean_url)
                                    queue.append((clean_url, depth + 1))
                except (httpx.RequestError, httpx.HTTPStatusError):
                    continue
    except (httpx.RequestError, httpx.HTTPStatusError):
        pass

    return sorted(discovered_urls)
