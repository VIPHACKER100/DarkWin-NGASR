import asyncio
import subprocess
import os
from typing import Optional, List, Dict, Any
from core.logging_system import get_logger

logger = get_logger("OneLinerAdapter")

class OneLinerAdapter:
    """
    Utility class to safely execute complex shell pipelines 
    within the DARKWIN asynchronous environment.
    """
    
    @staticmethod
    async def run_pipeline(pipeline: str, timeout: int = 600) -> Dict[str, Any]:
        """
        Executes a shell pipeline and returns the output.
        
        Args:
            pipeline: The shell command/pipeline to execute.
            timeout: Maximum execution time in seconds.
            
        Returns:
            Dictionary containing stdout, stderr, and exit_code.
        """
        logger.debug(f"Executing pipeline: {pipeline}")
        
        try:
            # On Windows, we use powershell or cmd, but many bug bounty tools 
            # assume a bash-like environment. We'll try to use the system shell.
            shell = True
            executable = None
            
            # If on Windows, we might need to wrap it differently or assume WSL/Cygwin/GitBash
            if os.name == 'nt':
                # Attempt to use powershell if possible, but standard shell usually works
                pass

            process = await asyncio.create_subprocess_shell(
                pipeline,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                executable=executable
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                return {
                    "stdout": stdout.decode(errors='ignore'),
                    "stderr": stderr.decode(errors='ignore'),
                    "exit_code": process.returncode
                }
            except asyncio.TimeoutError:
                process.kill()
                logger.error(f"Pipeline timed out after {timeout}s: {pipeline}")
                return {"stdout": "", "stderr": "Timeout", "exit_code": -1}
                
        except Exception as e:
            logger.error(f"Error executing pipeline: {e}")
            return {"stdout": "", "stderr": str(e), "exit_code": 1}

    @staticmethod
    def get_tool_path(config: dict, tool_name: str) -> str:
        """Get the path to a tool from the config or return tool_name if not found."""
        return config.get("tools", {}).get(tool_name, tool_name)
