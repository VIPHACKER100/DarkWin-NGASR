"""DARKWIN False Positive Filter with Security Hardening

Uses AI to identify false positive findings with secure HTTP data handling.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Dict, Optional
from core.config_manager import get_config
from core.logging_system import get_logger
from ai.security_utils import sanitize_prompt, validate_llm_response
from ai.ai_agent_manager import AIAgentManager
from integrations.api_utils import APIError, validate_api_key

logger = get_logger("AI.FalsePositiveFilter")
config = get_config()

# Constants
DEFAULT_MODEL: str = "gpt-4"
DEFAULT_TIMEOUT: int = 30
MAX_HTTP_DATA_LENGTH: int = 2000  # Limit HTTP data sent to LLM


def is_false_positive(finding: Dict[str, str], request_response_pair: Dict[str, str]) -> bool:
    """Determine if a finding is a false positive using AI with security hardening.

    Sanitizes HTTP data before sending to LLM to prevent information disclosure.
    Validates responses and handles errors securely.

    Args:
        finding: Dictionary containing vulnerability details
        request_response_pair: Dictionary with 'request' and 'response' keys

    Returns:
        True if the finding is likely a false positive, False otherwise
    """
    # Validate API key
    api_key = config.ai.api_key or config.ai.openai_api_key
    if not api_key:
        logger.warning("No OpenAI API key configured, cannot filter false positives")
        return False

    try:
        validate_api_key(api_key, "OpenAI")
    except ValueError as e:
        logger.error(f"Invalid OpenAI API key: {e}")
        return False

    # Sanitize finding data
    vuln_type = sanitize_prompt(finding.get('vuln_type', 'Unknown'))
    payload = sanitize_prompt(finding.get('payload', 'N/A'))

    if not vuln_type:
        logger.error("Vulnerability type sanitization failed")
        return False

    # Sanitize HTTP data (limit length and remove sensitive headers)
    request_data = _sanitize_http_data(request_response_pair.get('request', ''), 'request')
    response_data = _sanitize_http_data(request_response_pair.get('response', ''), 'response')

    # Create secure prompt
    prompt = f"""
    Evaluate if this security finding is a FALSE POSITIVE based on HTTP traffic analysis.

    Finding Type: {vuln_type}
    Payload Used: {payload}

    HTTP Request (sanitized):
    {request_data}

    HTTP Response (sanitized):
    {response_data}

    Instructions:
    - Consider if the payload actually caused a vulnerability or was just reflected
    - Check if error handling is proper vs. actual vulnerability
    - Look for signs of WAF blocking, input validation, or normal application behavior

    Return only 'TRUE' if this is clearly a false positive, or 'FALSE' if it appears to be a valid finding.
    """

    try:
        # Use unified AI Agent Manager
        agent = AIAgentManager(timeout=DEFAULT_TIMEOUT)
        
        result = agent.ask_agent(
            prompt=prompt,
            system_prompt="You are a cybersecurity expert analyzing HTTP traffic for false positives."
        )

        if not result or result.startswith("Error:"):
            logger.error(f"AI Agent returned error or empty response: {result}")
            return False

        # Parse result
        result_clean = result.strip().upper()
        is_false_positive_result = "TRUE" in result_clean

        logger.info(f"False positive analysis result: {is_false_positive_result}")
        return is_false_positive_result

    except (APIError, ValueError, httpx.RequestError) as e:
        logger.error(f"Unexpected error in false positive filtering: {e}", exc_info=True)
        return False


def _sanitize_http_data(http_data: str, data_type: str) -> str:
    """Sanitize HTTP request/response data for safe LLM processing.

    Removes sensitive headers, limits length, and sanitizes content.

    Args:
        http_data: Raw HTTP data string
        data_type: 'request' or 'response'

    Returns:
        Sanitized HTTP data safe for LLM processing
    """
    if not http_data:
        return "No data available"

    try:
        # Convert to string if not already
        data_str = str(http_data)

        # Remove sensitive headers
        sensitive_headers = [
            'authorization', 'cookie', 'set-cookie', 'x-api-key',
            'x-auth-token', 'authentication', 'proxy-authorization'
        ]

        lines = data_str.split('\n')
        sanitized_lines = []

        for line in lines:
            line_lower = line.lower()
            if any(f'{header}:' in line_lower for header in sensitive_headers):
                # Replace sensitive header values
                if ':' in line:
                    header_name = line.split(':', 1)[0]
                    sanitized_lines.append(f"{header_name}: [REDACTED]")
            else:
                sanitized_lines.append(line)

        # Rejoin and limit length
        sanitized = '\n'.join(sanitized_lines)
        if len(sanitized) > MAX_HTTP_DATA_LENGTH:
            sanitized = sanitized[:MAX_HTTP_DATA_LENGTH] + "\n[TRUNCATED]"

        # Final sanitization
        return sanitize_prompt(sanitized) or "Data sanitization failed"

    except (ValueError, OSError) as e:
        logger.warning(f"Error sanitizing HTTP {data_type} data: {e}")
        return f"Error sanitizing {data_type} data"
