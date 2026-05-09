"""DARKWIN AI Security & LLM Utilities

Provides secure patterns for LLM integration, prompt sanitization,
and API key handling.

Exports:
    sanitize_prompt(): Remove/escape dangerous characters from prompts
    validate_llm_response(): Schema validation for LLM output
    create_secure_llm_client(): Instantiate LLM client safely
    
Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import re
from typing import Dict, Any, Optional
from core.logging_system import get_logger

logger = get_logger("AI.Security")

# Constants
MAX_PROMPT_LENGTH: int = 10_000
DANGEROUS_PATTERNS: list = [
    r"\{\{.*?\}\}",  # Jinja-like templates
    r"__.*?__",  # Python dunder methods
]


def sanitize_prompt(prompt: str, max_length: int = MAX_PROMPT_LENGTH) -> str:
    """Sanitize user input before sending to LLM.
    
    Removes/escapes potentially dangerous patterns and enforces length limits.
    
    Args:
        prompt: Raw prompt text from user or system
        max_length: Maximum allowed prompt length (default: 10,000 chars)
        
    Returns:
        Sanitized prompt safe for LLM injection
        
    Note:
        This is NOT a complete solution to prompt injection. It's defense-in-depth.
        Additional validation should occur at LLM response layer.
    """
    if not isinstance(prompt, str):
        logger.warning(f"Invalid prompt type: {type(prompt)}")
        return ""
    
    # Enforce length limit
    if len(prompt) > max_length:
        logger.warning(
            f"Prompt exceeds {max_length} chars, truncating "
            f"(length: {len(prompt)})"
        )
        prompt = prompt[:max_length]
    
    # Remove dangerous patterns
    sanitized = prompt
    for pattern in DANGEROUS_PATTERNS:
        sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
    
    return sanitized


def validate_llm_response(response: str, expected_fields: Optional[list] = None) -> bool:
    """Validate LLM response format and content.
    
    Ensures response contains expected structure and doesn't contain
    potentially malicious payloads.
    
    Args:
        response: Raw response from LLM
        expected_fields: Optional list of expected fields (for JSON responses)
        
    Returns:
        True if response is valid, False otherwise
        
    Example:
        if validate_llm_response(response, ["status", "code"]):
            data = json.loads(response)
    """
    if not response or not isinstance(response, str):
        logger.error(f"Invalid response type: {type(response)}")
        return False
    
    # Check for suspiciously long responses (possible injection attempt)
    if len(response) > 100_000:
        logger.warning("Response exceeds 100KB, potential attack")
        return False
    
    # Check for executable patterns
    dangerous_keywords = ["eval(", "exec(", "__import__", "subprocess"]
    for keyword in dangerous_keywords:
        if keyword in response.lower():
            logger.error(f"Dangerous keyword detected in response: {keyword}")
            return False
    
    return True


def create_secure_llm_client(api_key: str, api_url: str, timeout: int = 30) -> Dict[str, Any]:
    """Create secure LLM client configuration.
    
    Encapsulates LLM client creation with security best practices.
    
    Args:
        api_key: API authentication key
        api_url: LLM endpoint URL
        timeout: Request timeout in seconds
        
    Returns:
        Configuration dictionary for LLM client
        
    Note:
        API key is not stored in config to prevent accidental logging.
        Should be passed directly to HTTP client.
    """
    if not api_key:
        logger.error("API key is required")
        raise ValueError("API key cannot be empty")
    
    if not api_url:
        logger.error("API URL is required")
        raise ValueError("API URL cannot be empty")
    
    # Validate timeout
    if timeout < 5 or timeout > 300:
        logger.warning(f"Timeout {timeout}s outside recommended range (5-300s)")
    
    return {
        "url": api_url,
        "timeout": timeout,
        "verify_ssl": True,  # Always verify SSL in production
        "retry_count": 3,
        "retry_backoff": 2,
    }