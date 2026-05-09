"""DARKWIN Ghost Mode (Stealth & Evasion)

Provides utilities for randomized fingerprints, User-Agents, 
and timing jitter to bypass WAFs and EDRs.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import random
import time
from typing import Dict

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

def get_random_user_agent() -> str:
    """Return a random modern User-Agent string."""
    return random.choice(USER_AGENTS)

def get_stealth_headers() -> Dict[str, str]:
    """Generate a set of randomized request headers."""
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

def apply_jitter(base_delay: float = 1.0, variation: float = 0.5):
    """Wait for a randomized duration using Gaussian distribution to avoid detection.
    
    Args:
        base_delay: Mean delay in seconds.
        variation: Standard deviation of the delay.
    """
    delay = random.gauss(base_delay, variation)
    # Ensure delay is within reasonable bounds (min 0.1s, max base + 3*variation)
    delay = max(0.1, min(delay, base_delay + (3 * variation)))
    time.sleep(delay)

def rotate_tls_config() -> Dict[str, any]:
    """Generate randomized TLS configuration to defeat JA3 fingerprinting.
    
    Returns:
        Dict compatible with httpx or custom SSL context builders.
    """
    # Common cipher suites used by modern browsers
    CIPHER_SUITES = [
        "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305",
        "DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384"
    ]
    
    # Randomize the order and selection
    selected_ciphers = random.sample(CIPHER_SUITES, random.randint(2, len(CIPHER_SUITES)))
    
    return {
        "ciphers": ":".join(selected_ciphers),
        "min_version": "TLSv1.2",
        "max_version": "TLSv1.3",
        "alpn_protocols": ["h2", "http/1.1"]
    }

def randomize_case(text: str) -> str:
    """Randomize the case of a string (useful for bypassing simple regex WAFs)."""
    return "".join(c.upper() if random.random() > 0.5 else c.lower() for c in text)

