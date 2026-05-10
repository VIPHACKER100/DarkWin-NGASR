"""DARKWIN AI Agent Manager with Security Hardening

Manages communication with LLM backends (OpenAI, local Ollama).
Implements secure prompt handling, timeout management, and error handling.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import httpx
import asyncio
from typing import Optional
from core.config_manager import get_config
from core.logging_system import get_logger
from core.module_loader import get_module_descriptions
from ai.security_utils import sanitize_prompt, validate_llm_response, create_secure_llm_client
from integrations.api_utils import APIError

logger = get_logger("AI.AgentManager")

# Constants
DEFAULT_TIMEOUT: int = 30
MAX_RETRIES: int = 3


class AIAgentManager:
    """Manages LLM queries with security best practices.

    Implements:
    - Prompt sanitization (injection prevention)
    - Response validation
    - Timeout enforcement
    - Structured error handling
    - API key security

    Attributes:
        config: Application configuration
        api_url: LLM endpoint URL
        timeout: Request timeout in seconds
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Initialize AI Agent Manager.

        Args:
            timeout: Request timeout in seconds (default: 30)
        """
        self.config = get_config()
        self.timeout: int = timeout
        self.logger = logger
        
        # Determine Backend & URL
        if self.config.ai.nvidia_api_key:
            self.backend = "nvidia"
            self.api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
            self.model = "google/gemma-3n-e4b-it"
        elif self.config.ai.openai_api_key:
            self.backend = "openai"
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.model = self.config.ai.openai_model
        else:
            self.backend = "local"
            self.api_url = self.config.ai.local_llm_url.rstrip("/") + "/chat/completions"
            self.model = self.config.ai.openai_model

        # Validate configuration
        if not self.api_url:
            self.logger.error("AI LLM URL not configured")
            raise ValueError("AI LLM URL not configured in config.yaml")

    def ask_agent(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Query the LLM with security hardening and registry context."""
        
        # 0. Build dynamic system prompt if not provided
        if not system_prompt:
            available_modules = get_module_descriptions()
            system_prompt = f"""
            You are DARKWIN AI, an elite autonomous security research agent.
            
            AVAILABLE MODULES:
            {available_modules}
            
            CONSTRAINTS:
            - Only suggest modules from the list provided above.
            - You MUST use the exact string from the 'ID' field when recommending a module.
            - Format your plan as a structured pipeline.
            - Ensure modules selected match the target technology.
            """

        # 1. Sanitize prompt before sending
        safe_prompt = sanitize_prompt(prompt)
        if not safe_prompt:
            self.logger.error("Prompt sanitization failed or empty")
            return "Error: Invalid prompt"

        # 2. Prepare request
        headers: dict = {}
        if self.backend == "nvidia":
            headers["Authorization"] = f"Bearer {self.config.ai.nvidia_api_key}"
            headers["Accept"] = "application/json"
        elif self.backend == "openai":
            headers["Authorization"] = f"Bearer {self.config.ai.openai_api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": safe_prompt}
            ],
            "temperature": 0.2,
            "top_p": 0.7
        }

        # 3. Execute request with timeout
        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                with httpx.Client(timeout=self.timeout, verify=True) as client:
                    response = client.post(
                        self.api_url,
                        json=payload,
                        headers=headers
                    )

                    # Check response status
                    if response.status_code == 429:
                        # Rate limited
                        wait_time = int(response.headers.get("Retry-After", "2"))
                        self.logger.warning(
                            f"Rate limited. Retry after {wait_time}s"
                        )
                        raise APIError(
                            "Rate limited",
                            status_code=429,
                            retry_after=wait_time
                        )

                    if response.status_code != 200:
                        raise APIError(
                            f"LLM returned {response.status_code}",
                            status_code=response.status_code
                        )

                    # 4. Validate response format
                    response_data = response.json()
                    if not validate_llm_response(str(response_data)):
                        self.logger.error("Response validation failed")
                        raise APIError("Invalid LLM response format")

                    # 5. Extract content
                    content = response_data.get("choices", [{}])[0] \
                        .get("message", {}) \
                        .get("content", "")

                    if not content:
                        self.logger.error("No content in LLM response")
                        raise APIError("Empty response from LLM")

                    self.logger.info("LLM query successful")
                    return content

            except httpx.TimeoutException as e:
                self.logger.warning(
                    f"LLM request timeout ({self.timeout}s), retry {retry_count + 1}"
                )
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    raise APIError("LLM request timeout after retries") from e

            except APIError as e:
                self.logger.error(f"LLM API error: {e.message}")
                if not e.should_retry or retry_count >= MAX_RETRIES:
                    return f"Error: {e.message}"
                retry_count += 1

            except ValueError as e:
                self.logger.error(f"Invalid JSON response: {e}")
                return f"Error: Invalid response format"

            except Exception as e:
                err_msg = str(e)
                if "10061" in err_msg or "connection refused" in err_msg.lower():
                    self.logger.error("AI Backend Offline: No connection could be made to the local LLM server.")
                    self.logger.info("👉 HINT: Start Ollama (ollama serve) or configure an OpenAI/NVIDIA API key.")
                    return "Error: AI Backend Offline (Ollama/Local LLM not responding)"
                
                self.logger.error(
                    f"Unexpected error querying LLM: {err_msg}",
                    exc_info=True
                )
                return f"Error: {err_msg}"

        return "Error: LLM query failed after retries"

    async def async_ask_agent(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Query the LLM asynchronously with security hardening and registry context. """
        
        # 0. Build dynamic system prompt if not provided
        if not system_prompt:
            available_modules = get_module_descriptions()
            system_prompt = f"""
            You are DARKWIN AI, an elite autonomous security research agent.
            
            AVAILABLE MODULES:
            {available_modules}
            
            CONSTRAINTS:
            - Only suggest modules from the list provided above.
            - You MUST use the exact string from the 'ID' field when recommending a module.
            - Use the EXACT names provided in the list.
            - Formulate a logical multi-step attack plan.
            """

        # 1. Sanitize prompt
        safe_prompt = sanitize_prompt(prompt)
        if not safe_prompt:
            self.logger.error("Prompt sanitization failed")
            return "Error: Invalid prompt"

        # 2. Prepare request
        headers: dict = {}
        if self.backend == "nvidia":
            headers["Authorization"] = f"Bearer {self.config.ai.nvidia_api_key}"
            headers["Accept"] = "application/json"
        elif self.backend == "openai":
            headers["Authorization"] = f"Bearer {self.config.ai.openai_api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": safe_prompt}
            ],
            "temperature": 0.2,
            "top_p": 0.7
        }

        # 3. Execute request asynchronously
        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                async with httpx.AsyncClient(timeout=self.timeout, verify=True) as client:
                    response = await client.post(
                        self.api_url,
                        json=payload,
                        headers=headers
                    )

                    if response.status_code == 200:
                        response_data = response.json()
                        if validate_llm_response(str(response_data)):
                            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                            if content:
                                self.logger.info("Async LLM query successful")
                                return content
                        
                        raise APIError("Invalid or empty LLM response")
                    
                    if response.status_code == 429:
                        wait_time = int(response.headers.get("Retry-After", "2"))
                        await asyncio.sleep(wait_time)
                        retry_count += 1
                        continue

                    raise APIError(f"LLM returned {response.status_code}")

            except Exception as e:
                self.logger.warning(f"Async LLM query attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    return f"Error: {str(e)}"
                await asyncio.sleep(2)

        return "Error: Async LLM query failed"


def analyze_vulnerability(finding: dict) -> str:
    """Analyze a vulnerability finding with AI.

    Args:
        finding: Finding dictionary with vuln_type, description, etc.

    Returns:
        AI analysis of the vulnerability
    """
    try:
        manager = AIAgentManager()
        prompt = f"""
        Analyze this security vulnerability:
        Type: {finding.get('vuln_type', 'Unknown')}
        Description: {finding.get('description', 'N/A')}

        Provide:
        1. Potential impact (1-2 sentences)
        2. Exploitation complexity
        3. Recommended remediation
        """
        return manager.ask_agent(prompt)
    except Exception as e:
        logger.error(f"Vulnerability analysis failed: {e}", exc_info=True)
        return f"Analysis failed: {str(e)}"
