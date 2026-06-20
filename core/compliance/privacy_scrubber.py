"""DARKWIN Privacy Scrubber compliance module.

Removes PII and sensitive data from text using regex patterns
to ensure privacy compliance before data persistence or transmission.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import re
from typing import Dict

PII_PATTERNS: Dict[str, str] = {
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "PHONE": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "AWS_KEY": r"\bAKIA[0-9A-Z]{16}\b",
    "SECRET_KEY": r"(?i)(?:key|secret|password|auth|token|api_key|apikey)[ \t]*[:=][ \t]*[^\s\"'\n]{10,}",
    "JWT_TOKEN": r"ey[a-zA-Z0-9_-]+\.ey[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
}


def scrub_pii(text: str, custom_label: str = "REDACTED") -> str:
    """Remove PII and sensitive data from text.

    Args:
        text: The input string to scrub.
        custom_label: Label used for redaction placeholders.

    Returns:
        The scrubbed text with all PII patterns replaced.
    """
    if not text:
        return ""

    scrubbed_text = text
    for name, pattern in PII_PATTERNS.items():
        label = f"[{name}_{custom_label}]"
        scrubbed_text = re.sub(pattern, label, scrubbed_text)

    return scrubbed_text

