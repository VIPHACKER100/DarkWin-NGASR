"""DARKWIN Interactive Shell

Provides a custom REPL/Shell for DARKWIN-NGASR, allowing for rapid 
command execution and session management in a high-fidelity 
terminal environment.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
import sys

console = Console()

class DarkWinShell:
    """Interactive CLI shell for DARKWIN."""
    
    def __init__(self):
        self.commands = {
            "hunt": "Start autonomous scan",
            "targets": "Manage target scope list",
            "history": "View recent scan history",
            "wordlists": "Manage security wordlists",
            "payloads": "View exploit payloads",
            "screenshots": "View captured evidence",
            "mesh": "View distributed nodes",
            "proxy": "Manage proxy pool",
            "report": "Generate AI reports",
            "schedule": "Manage periodic tasks",
            "logs": "View system logs",
            "config": "View/edit configuration",
            "modules": "List all scan modules",
            "doctor": "Run diagnostics",
            "test": "Run core unit tests",
            "update": "Update ecosystem from GitHub",
            "update-templates": "Sync Nuclei templates",
            "about": "Project info",
            "clear": "Clear screen",
            "exit": "Exit shell"
        }
        self.completer = WordCompleter(list(self.commands.keys()), ignore_case=True)
        self.style = Style.from_dict({
            'prompt': '#00ffff bold',
            'command': '#ff00ff',
        })

    def print_welcome(self):
        logo = """
   ________    ____  _______       _______ _   __
  / ____/ /   / __ \/ ____/ |     / /  _/ | / /
 / /   / /   / / / / __/  | | /| / // / /  |/ / 
/ /___/ /___/ /_/ / /___  | |/ |/ // / / /|  /  
\____/_____/\____/_____/  |__/|__/___/_/ |_/   
        """
        console.print(Text(logo, style="bold magenta"))
        console.print("[bold cyan]Welcome to the DARKWIN Autonomous Shell[/bold cyan]")
        console.print("Type 'help' for commands or 'exit' to quit.\n")

    async def start(self):
        from rich.text import Text
        self.print_welcome()
        session = PromptSession(completer=self.completer, style=self.style)
        
        while True:
            try:
                cmd_line = await session.prompt_async([('class:prompt', 'darkwin > ')])
                if not cmd_line.strip(): continue
                
                parts = cmd_line.split()
                cmd = parts[0].lower()
                
                if cmd == "exit" or cmd == "quit":
                    break
                elif cmd == "help":
                    self.show_help()
                elif cmd == "clear":
                    console.clear()
                elif cmd in self.commands:
                    # Run the click command manually
                    from core.command_router import cli
                    try:
                        cli.main(args=parts, standalone_mode=False)
                    except Exception as e:
                        console.print(f"[red]Error executing command: {e}[/red]")
                else:
                    console.print(f"[yellow]Unknown command: {cmd}[/yellow]")
                    
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    def show_help(self):
        from rich.table import Table
        table = Table(title="Available Commands", border_style="cyan")
        table.add_column("Command", style="magenta")
        table.add_column("Description", style="white")
        for c, d in self.commands.items():
            table.add_row(c, d)
        console.print(table)

if __name__ == "__main__":
    import asyncio
    shell = DarkWinShell()
    asyncio.run(shell.start())
