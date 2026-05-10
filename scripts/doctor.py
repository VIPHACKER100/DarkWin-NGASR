import sys
import os
import subprocess
import shutil
import socket
import logging
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from core.config_manager import get_config

console = Console()

def check_python():
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor} (3.10+ required)"

def check_package(package_name):
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False

def check_external_tool(tool_name):
    return shutil.which(tool_name) is not None

def check_redis():
    config = get_config()
    import redis
    try:
        r = redis.from_url(config.redis.url, socket_timeout=1)
        r.ping()
        return True, "Connected"
    except Exception as e:
        return False, str(e)

def check_database():
    config = get_config()
    from sqlalchemy import create_engine, text
    try:
        engine = create_engine(config.database.url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Connected"
    except Exception as e:
        return False, str(e)

def run_doctor():
    console.print(Panel("[bold cyan]DARKWIN System Diagnostic Tool[/bold cyan]\n[dim]Developed by VIPHACKER.100[/dim]", expand=False))
    
    # 1. Environment
    table = Table(title="1. Core Environment", expand=True)
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details")
    
    py_ok, py_msg = check_python()
    table.add_row("Python Version", "[green]OK" if py_ok else "[red]FAIL", py_msg)
    
    # 2. Key Dependencies
    packages = ["flask", "sqlalchemy", "redis", "celery", "rich", "pydantic", "openai"]
    for pkg in packages:
        ok = check_package(pkg)
        table.add_row(f"Package: {pkg}", "[green]OK" if ok else "[red]MISSING", "")
    
    console.print(table)
    
    # 3. External Tools
    config = get_config()
    tools_table = Table(title="2. External Security Tools", expand=True)
    tools_table.add_column("Tool", style="cyan")
    tools_table.add_column("Path", style="bold")
    tools_table.add_column("Status")
    
    tools = ["nmap", "subfinder", "httpx", "nuclei", "ffuf", "sqlmap"]
    tool_status = {}
    for tool in tools:
        path = shutil.which(tool)
        is_ok = path is not None
        tool_status[tool] = is_ok
        tools_table.add_row(tool, path if path else "Not found", "[green]OK" if is_ok else "[yellow]WARN")
    
    console.print(tools_table)
    
    # 4. Infrastructure
    infra_table = Table(title="3. Infrastructure Services", expand=True)
    infra_table.add_column("Service", style="cyan")
    infra_table.add_column("Status", style="bold")
    infra_table.add_column("Error/Details")
    
    red_ok, red_msg = check_redis()
    infra_table.add_row("Redis", "[green]OK" if red_ok else "[red]OFFLINE", red_msg)
    
    db_ok, db_msg = check_database()
    infra_table.add_row("Database", "[green]OK" if db_ok else "[red]OFFLINE", db_msg)
    
    console.print(infra_table)
    
    # 5. Dashboard
    dash_table = Table(title="4. Dashboard (Frontend)", expand=True)
    dash_table.add_column("Check", style="cyan")
    dash_table.add_column("Status", style="bold")
    
    node_ok = check_external_tool("node")
    npm_ok = check_external_tool("npm")
    dash_table.add_row("Node.js", "[green]OK" if node_ok else "[red]MISSING")
    dash_table.add_row("NPM", "[green]OK" if npm_ok else "[red]MISSING")
    
    console.print(dash_table)

    # 6. Repair Hints
    hints = Table(title="💡 Repair Instructions (Windows/Choco)", expand=True, border_style="yellow")
    hints.add_column("Issue", style="cyan")
    hints.add_column("Recommended Command", style="green")
    
    if not red_ok:
        hints.add_row("Redis Offline", "choco install redis-64  (then: redis-server)")
    if not tool_status.get("nmap"):
        hints.add_row("Nmap Missing", "choco install nmap")
    if not tool_status.get("sqlmap"):
        hints.add_row("Sqlmap Missing", "choco install sqlmap")
    
    # Check for missing go tools if choco doesn't have them easily
    missing_tools = [t for t in ["subfinder", "nuclei", "ffuf"] if not check_external_tool(t)]
    if missing_tools:
        hints.add_row("Go Tools Missing", "choco install golang  (then: make setup-tools)")

    if hints.rows:
        console.print(hints)

    console.print("\n[bold yellow]Diagnostic Complete.[/bold yellow]")
    if not (py_ok and red_ok and db_ok and node_ok):
        console.print("[red]Some critical components are missing or offline. Use the hints above to fix them.[/red]")
    else:
        console.print("[bold green]All systems go! DARKWIN is ready for autonomous hunting.[/bold green]")

if __name__ == "__main__":
    run_doctor()
