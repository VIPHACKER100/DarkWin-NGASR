import os
import sys
from rich.console import Console
from rich.panel import Panel
from core.config_manager import validate_config, get_config
from core.logging_system import get_logger
from core.command_router import cli

console = Console()
logger = get_logger("Main")

BANNER = """
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

def check_legal():
    """Ensure LEGAL.md has been acknowledged"""
    flag_file = ".acknowledged"
    if not os.path.exists(flag_file):
        console.print(Panel.fit(
            "[bold red]WARNING: LEGAL ACKNOWLEDGEMENT REQUIRED[/bold red]\n\n"
            "By using DARKWIN, you agree to the terms in [bold]LEGAL.md[/bold].\n"
            "This tool is for [bold green]AUTHORIZED USE ONLY[/bold green].\n\n"
            "Do you acknowledge and accept these terms? (y/n)",
            title="Legal Disclaimer"
        ))
        choice = input("> ").lower()
        if choice == 'y':
            with open(flag_file, 'w') as f:
                f.write("acknowledged")
            console.print("[bold green]Acknowledgement saved.[/bold green]")
        else:
            console.print("[bold red]Access denied. You must accept the legal terms.[/bold red]")
            sys.exit(1)

def main():
    try:
        # 1. Print Banner
        console.print(BANNER)
        
        # 2. Check Legal
        check_legal()
        
        # 3. Validate Config
        validate_config()
        
        # 4. Run CLI
        cli()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
