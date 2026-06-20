"""
DARKWIN One-Liner Pipeline Adapter

Utility to safely execute complex shell pipelines within the DARKWIN
asynchronous environment with timeout enforcement.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: MIT
"""

import asyncio
import os
from typing import Dict, Any
from core.logging_system import get_logger

logger = get_logger("OneLinerAdapter")


class OneLinerAdapter:
    """Safely executes shell pipelines in the DARKWIN async environment."""

    @staticmethod
    async def run_pipeline(pipeline: str, timeout: int = 600) -> Dict[str, Any]:
        """Execute a shell pipeline and return the output.

        Args:
            pipeline: The shell command or pipeline to execute.
            timeout: Maximum execution time in seconds (default 600).

        Returns:
            Dict with stdout, stderr, and exit_code keys.
        """
        logger.debug(f"Executing pipeline: {pipeline}")

        try:
            process = await asyncio.create_subprocess_shell(
                pipeline,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                return {
                    "stdout": stdout.decode(errors='ignore'),
                    "stderr": stderr.decode(errors='ignore'),
                    "exit_code": process.returncode or 0
                }
            except asyncio.TimeoutError:
                process.kill()
                logger.error(f"Pipeline timed out after {timeout}s: {pipeline}")
                return {"stdout": "", "stderr": "Timeout", "exit_code": -1}

        except OSError as e:
            logger.error(f"OS error executing pipeline: {e}")
            return {"stdout": "", "stderr": str(e), "exit_code": 1}

    @staticmethod
    def get_tool_path(config: dict, tool_name: str) -> str:
        """Get the path to a tool from config or return the tool name as fallback.

        Args:
            config: Application configuration dict.
            tool_name: Name of the tool to look up.

        Returns:
            Configured tool path or the tool name if not found.
        """
        return config.get("tools", {}).get(tool_name, tool_name)
