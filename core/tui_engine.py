"""DARKWIN Terminal User Interface (TUI) Engine

Creates a premium, real-time dashboard in the terminal using Rich.
Visualizes agent reasoning, findings, and mesh status.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from datetime import datetime

class DarkWinTUI:
    """Real-time terminal dashboard for DARKWIN."""
    
    def __init__(self, target: str):
        self.target = target
        self.layout = Layout()
        self.console = Console()
        self.reasoning = "Initializing reasoning engine..."
        self.findings = []
        self.step = 0
        self.max_steps = 0
        self.status = "Preparing..."

    def make_layout(self) -> Layout:
        """Define the dashboard grid."""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right", ratio=2)
        )
        self.layout["left"].split_column(
            Layout(name="status"),
            Layout(name="reasoning", ratio=2)
        )
        return self.layout

    def update_header(self):
        text = Text(f"🛡️ DARKWIN-NGASR | Target: {self.target} | {datetime.now().strftime('%H:%M:%S')}", style="bold cyan")
        return Panel(text, border_style="cyan")

    def update_status(self):
        table = Table.grid(expand=True)
        table.add_row("Status:", f"[bold green]{self.status}[/bold green]")
        table.add_row("Step:", f"[bold yellow]{self.step}/{self.max_steps}[/bold yellow]")
        return Panel(table, title="System State", border_style="green")

    def update_reasoning(self):
        return Panel(Text(self.reasoning, style="italic dim"), title="🧠 Agent Reasoning", border_style="magenta")

    def update_findings(self):
        table = Table(title="💎 Discovered Findings", expand=True)
        table.add_column("Time", style="dim")
        table.add_column("Severity", style="bold")
        table.add_column("Type", style="cyan")
        table.add_column("Endpoint", style="white")
        
        for f in self.findings[-10:]: # Show last 10
            severity_style = "red" if f['severity'] == 'Critical' else "yellow"
            table.add_row(
                f['time'],
                f"[{severity_style}]{f['severity']}[/{severity_style}]",
                f['type'],
                f['endpoint']
            )
        return Panel(table, border_style="white")

    def render(self):
        self.layout["header"].update(self.update_header())
        self.layout["status"].update(self.update_status())
        self.layout["reasoning"].update(self.update_reasoning())
        self.layout["right"].update(self.update_findings())
        self.layout["footer"].update(Panel(Text("VIPHACKER.100 | Autonomous Research Mode Active", style="dim center")))
        return self.layout
