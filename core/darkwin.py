"""DARKWIN Main Entry Point

This module initializes the DARKWIN platform, validates configuration,
and enforces legal acknowledgement before execution.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import os
import sys
from pathlib import Path
from typing import NoReturn

# Add project root to sys.path to support absolute imports (from core.xxx)
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from rich.console import Console
from rich.panel import Panel

from core.config_manager import validate_config, get_config
from core.logging_system import get_logger
from core.command_router import cli

console: Console = Console()
logger = get_logger("Main")

BANNER = r"""
[bold cyan]
  _____            _____  _  ___          _______ _   _ 
 |  __ \     /\   |  __ \| |/ \ \        / /_   _| \ | |
 | |  | |   /  \  | |__) | ' / \ \  /\  / /  | | |  \| |
 | |  | |  / /\ \ |  _  /|  <   \ \/  \/ /   | | | . ` |
 | |__| | / ____ \| | \ \| . \   \  /\  /   _| |_| |\  |
 |_____/ /_/    \_\_|  \_\_|\_\   \/  \/   |_____|_| \_|
[/bold cyan]
  [bold white]Next-Generation Automated Security Research Platform[/bold white]
  [dim]Developed by ARYAN AHIRWAR (VIPHACKER.100)[/dim]
"""

def check_legal() -> None:
    """Ensure LEGAL.md has been acknowledged before execution.
    
    Displays legal disclaimer and requires explicit user acceptance.
    Stores acknowledgement in .acknowledged flag file.
    
    Raises:
        SystemExit: If user declines the legal terms (exit code 1).
    """
    flag_file: Path = Path(".acknowledged")
    
    if not flag_file.exists():
        console.print(Panel.fit(
            "[bold red]WARNING: LEGAL ACKNOWLEDGEMENT REQUIRED[/bold red]\n\n"
            "By using DARKWIN, you agree to the terms in [bold]LEGAL.md[/bold].\n"
            "This tool is for [bold green]AUTHORIZED USE ONLY[/bold green].\n\n"
            "Do you acknowledge and accept these terms? (y/n)",
            title="Legal Disclaimer"
        ))
        
        choice: str = input("> ").strip().lower()
        
        if choice == "y":
            flag_file.write_text("acknowledged")
            console.print("[bold green]Acknowledgement saved.[/bold green]")
        else:
            console.print("[bold red]Access denied. You must accept the legal terms.[/bold red]")
            sys.exit(1)

def main() -> NoReturn:
    """Main entry point for DARKWIN CLI application.
    
    Execution flow:
    1. Display banner and version info
    2. Verify legal acknowledgement
    3. Validate configuration
    4. Run CLI interface
    
    Raises:
        SystemExit: With appropriate exit code (0 success, 1 error).
    """
    try:
        # 1. Print Banner
        console.print(BANNER)
        
        # 2. Check Legal Acknowledgement
        check_legal()
        
        # 3. Validate Configuration
        validate_config()
        
        # 4. Run CLI Interface
        cli()
        
    except KeyboardInterrupt:
        logger.warning("User interrupted execution.")
        sys.exit(0)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
