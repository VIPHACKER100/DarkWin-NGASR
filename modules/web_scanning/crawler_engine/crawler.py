import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set

MODULE_META = {
    "name": "Web Crawler",
    "category": "Web Scanning",
    "description": "Async BFS web crawler to discover URLs within scope",
    "version": "1.0.0"
}

async def run(start_url: str, scan_id: str, config: dict, max_depth: int = 3, max_pages: int = 100) -> List[str]:
    """
    Async web crawler using httpx.
    """
    discovered_urls: Set[str] = set()
    queue: List[tuple] = [(start_url, 0)]
    domain = urlparse(start_url).netloc
    
    discovered_urls.add(start_url)
    
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            while queue and len(discovered_urls) < max_pages:
                current_url, depth = queue.pop(0)
                if depth > max_depth:
                    continue
                
                try:
                    response = await client.get(current_url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        for link in soup.find_all('a', href=True):
                            absolute_url = urljoin(current_url, link['href'])
                            parsed_url = urlparse(absolute_url)
                            
                            # Only stay within the same domain
                            if parsed_url.netloc == domain:
                                # Strip fragments
                                clean_url = absolute_url.split('#')[0].rstrip('/')
                                if clean_url not in discovered_urls:
                                    discovered_urls.add(clean_url)
                                    queue.append((clean_url, depth + 1))
                except Exception:
                    continue
    except Exception:
        pass
        
    return list(discovered_urls)
