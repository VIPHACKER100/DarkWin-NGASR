"""DARKWIN Multi-Step Reasoning Engine with Security Hardening

Performs tactical reasoning for scan planning with secure prompt handling.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from typing import Optional
from core.logging_system import get_logger
from ai.ai_agent_manager import AIAgentManager
from ai.security_utils import sanitize_prompt

logger = get_logger("AI.ReasoningEngine")


class ReasoningEngine:
    """Multi-step reasoning engine for tactical scan planning.

    Uses AI to analyze current context and recommend next security research steps
    with secure prompt handling and response validation.
    """

    def __init__(self) -> None:
        """Initialize the reasoning engine with secure AI agent."""
        try:
            self.agent = AIAgentManager()
            logger.info("Reasoning engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize reasoning engine: {e}")
            raise

    def perform_reasoning(self, context: str) -> str:
        """Perform multi-step reasoning to plan next scan steps.

        Sanitizes context input and validates AI responses for security.

        Args:
            context: Current security research context and findings

        Returns:
            AI-generated plan for next research steps, or error message
        """
        try:
            # Sanitize context to prevent prompt injection
            safe_context = sanitize_prompt(context)
            if not safe_context:
                logger.error("Context sanitization failed")
                return "Error: Invalid context data"

            # Create secure system prompt
            system_prompt = (
                "You are a tactical reasoning engine for DARKWIN security research. "
                "Analyze the current context and recommend the most effective next steps. "
                "Focus on logical progression and high-impact security testing. "
                "ALWAYS respond in structured JSON format."
            )

            # Create secure user prompt
            prompt = f"""
            Based on the current security research context below, recommend the next modules to run.
            
            Current Context:
            {safe_context}

            Respond ONLY with a JSON object in this format:
            {{
                "recommendations": [
                    {{
                        "module_name": "exact_module_name",
                        "reason": "why this module",
                        "priority": 1-5
                    }}
                ],
                "summary": "overall strategy"
            }}
            """

            # Get AI reasoning using secure agent
            response = self.agent.ask_agent(prompt, system_prompt=system_prompt)
            return response

        except Exception as e:
            logger.error(f"Error in multi-step reasoning: {e}", exc_info=True)
            return f"Error generating reasoning plan: {str(e)}"
