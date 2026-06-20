"""DARKWIN Automated Remediation with Security Hardening

Generates secure code remediation suggestions with response validation.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
from typing import Dict, Optional
from core.logging_system import get_logger
from ai.ai_agent_manager import AIAgentManager
from ai.security_utils import sanitize_prompt

logger = get_logger("AI.AutomatedRemediation")


def suggest_remediation(finding: Dict[str, str]) -> str:
    """Generate secure remediation advice for a vulnerability finding.

    Uses AI to provide code-level fixes with validation to ensure suggestions are safe.

    Args:
        finding: Dictionary containing vulnerability details

    Returns:
        AI-generated remediation suggestion, or error message if generation fails
    """
    try:
        # Sanitize input data
        vuln_type = sanitize_prompt(finding.get('vuln_type', 'Unknown'))
        description = sanitize_prompt(finding.get('description', 'No description available'))

        if not vuln_type:
            logger.error("Vulnerability type sanitization failed")
            return "Error: Invalid vulnerability data"

        # Create secure prompt for code generation
        prompt = f"""
        Provide a secure code remediation for this vulnerability:

        Vulnerability Type: {vuln_type}
        Description: {description}

        Requirements:
        1. Provide specific, secure code changes
        2. Include input validation and sanitization
        3. Use secure coding practices
        4. Explain the fix clearly
        5. Include before/after code examples if helpful

        Focus on practical, implementable solutions.
        """

        # Get AI suggestion using the secure agent manager
        agent = AIAgentManager()
        suggestion = agent.ask_agent(prompt)

        if not suggestion or suggestion.startswith("Error:"):
            logger.warning("AI remediation suggestion failed or returned error")
            return suggestion or "Unable to generate remediation suggestion"

        # Validate the generated code suggestion
        if not validate_code_suggestion(suggestion):
            logger.error("Generated remediation failed security validation")
            return "Error: Generated suggestion failed security validation"

        logger.info("Successfully generated secure remediation suggestion")
        return suggestion

    except (APIError, ValueError, httpx.RequestError) as e:
        logger.error(f"Error generating remediation suggestion: {e}", exc_info=True)
        return f"Error generating remediation: {str(e)}"


def validate_code_suggestion(suggestion: str) -> bool:
    """Validate that an AI-generated code suggestion is safe.

    Checks for dangerous patterns in generated code.

    Args:
        suggestion: The AI-generated code suggestion

    Returns:
        True if suggestion appears safe, False otherwise
    """
    if not suggestion:
        return False

    suggestion_lower = suggestion.lower()

    # Dangerous patterns to check for
    dangerous_patterns = [
        'eval(', 'exec(', '__import__', 'subprocess.call',
        'os.system', 'shell=true', 'dangerous', 'insecure',
        'bypass', 'exploit', 'hack', 'malicious'
    ]

    for pattern in dangerous_patterns:
        if pattern in suggestion_lower:
            logger.warning(f"Dangerous pattern detected in suggestion: {pattern}")
            return False

    return True
