"""DARKWIN System Diagnostic Utility

Provides automated checks for system dependencies, external tools,
database connectivity, and environment configuration.
Supports automated fixing of common issues.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import os
import shutil
import subprocess
import sys
from typing import List, Tuple

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import importlib.util

def check_pydantic_health() -> Tuple[bool, str]:
    """Check for typing_extensions shadowing issues."""
    try:
        import typing_extensions
        if not hasattr(typing_extensions, 'Sentinel'):
             return False, "typing_extensions version is too old (missing Sentinel). Shadowed by system?"
        import pydantic
        return True, "Healthy"
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

console: Console = Console()

from core.config_manager import get_config

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version meets minimum requirements."""
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        return True, version
    return False, version

def check_pip_dependencies() -> List[Tuple[str, bool]]:
    """Check if all required pip packages are installed."""
    results = []
    from importlib.metadata import version, PackageNotFoundError
    requirements_path = "requirements.txt"
    if not os.path.exists(requirements_path):
        return [("requirements.txt not found", False)]
    
    with open(requirements_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Simple check for package name
            package_name = line.split(">")[0].split("=")[0].split("<")[0].strip()
            try:
                version(package_name)
                results.append((package_name, True))
            except PackageNotFoundError:
                results.append((package_name, False))
    
    return results

def check_external_tools() -> List[Tuple[str, bool]]:
    """Check if required external security tools are in PATH."""
    config = get_config()
    tools = [
        config.tools.nmap,
        config.tools.subfinder,
        config.tools.httpx,
        config.tools.nuclei,
        config.tools.ffuf,
        config.tools.amass,
        config.tools.katana,
        config.tools.sqlmap,
        config.tools.dalfox,
        config.tools.masscan,
    ]
    
    results = []
    for tool in tools:
        path = shutil.which(tool)
        results.append((tool, path is not None))
    
    return results

def check_database() -> Tuple[bool, str]:
    """Check database connectivity (lazy — safe to call with no DB)."""
    try:
        from sqlalchemy import text
        from core.database import get_engine
        eng = get_engine()
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Connected"
    except Exception as e:
        return False, str(e)

def check_redis() -> Tuple[bool, str]:
    """Check Redis connectivity."""
    config = get_config()
    try:
        import redis
        r = redis.from_url(config.redis.url)
        r.ping()
        return True, "Connected"
    except ImportError:
        return False, "redis-py not installed"
    except Exception as e:
        return False, str(e)

def check_node_version() -> Tuple[bool, str]:
    """Check if Node.js is installed (required for dashboard)."""
    try:
        res = subprocess.run(["node", "--version"], capture_output=True, text=True)
        return True, res.stdout.strip()
    except Exception:
        return False, "Not Found"

def check_docker() -> Tuple[bool, str]:
    """Check if Docker is installed (required for orchestration)."""
    try:
        res = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        return True, res.stdout.strip()
    except Exception:
        return False, "Not Found"

def run_doctor(fix: bool = False) -> None:
    """Run all system diagnostics and optionally fix issues."""
    console.print(Panel.fit("[bold cyan]DARKWIN System Diagnostic (Doctor)[/bold cyan]"))
    
    # 1. Python Check
    py_ok, py_ver = check_python_version()
    console.print(f"Python Version: {py_ver} [{'green]OK[/green]' if py_ok else '[red]FAIL[/red]'}]")
    
    # 2. Pip Dependencies
    pip_results = check_pip_dependencies()
    missing_pip = [p for p, ok in pip_results if not ok]
    
    table_pip = Table(title="Python Dependencies")
    table_pip.add_column("Package", style="cyan")
    table_pip.add_column("Status", justify="center")
    
    for pkg, ok in pip_results:
        table_pip.add_row(pkg, "[green]Installed[/green]" if ok else "[red]Missing[/red]")
    
    console.print(table_pip)
    
    # 3. External Tools
    tool_results = check_external_tools()
    missing_tools = [t for t, ok in tool_results if not ok]
    
    table_tools = Table(title="External Security Tools")
    table_tools.add_column("Tool", style="magenta")
    table_tools.add_column("Status", justify="center")
    
    for tool, ok in tool_results:
        table_tools.add_row(tool, "[green]Found[/green]" if ok else "[red]Not Found[/red]")
    
    console.print(table_tools)
    
    # 4. Services
    db_ok, db_msg = check_database()
    redis_ok, redis_msg = check_redis()
    node_ok, node_ver = check_node_version()
    docker_ok, docker_ver = check_docker()
    pydantic_ok, pydantic_msg = check_pydantic_health()
    
    console.print("\n[bold]System Services & Environment:[/bold]")
    console.print(f"  Database: {db_msg} [{'green]OK[/green]' if db_ok else '[red]FAIL[/red]'}]")
    console.print(f"  Redis:    {redis_msg} [{'green]OK[/green]' if redis_ok else '[red]FAIL[/red]'}]")
    console.print(f"  Node.js:  {node_ver} [{'green]OK[/green]' if node_ok else '[red]FAIL[/red]'}]")
    console.print(f"  Docker:   {docker_ver} [{'green]OK[/green]' if docker_ok else '[red]FAIL[/red]'}]")
    console.print(f"  Pydantic: {pydantic_msg} [{'green]OK[/green]' if pydantic_ok else '[red]FAIL[/red]'}]")
    
    # 5. Fix Logic
    if fix:
        console.print("\n[bold yellow]Attempting to fix issues...[/bold yellow]")

        if not pydantic_ok:
            console.print("[bold yellow]⚠ Pydantic/typing_extensions shadowing detected.[/bold yellow]")
            console.print("[bold cyan]Best Fix — Use the project virtual environment:[/bold cyan]")
            console.print("  Run [green]./setup.sh[/green] then [green]source .venv/bin/activate[/green]")
            console.print("  Then retry: [green]darkwin --help[/green]\n")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade",
                            "typing-extensions>=4.11.0", "pydantic-core>=2.18.0"], check=False)

        if missing_pip:
            console.print(f"Installing missing Python packages: {', '.join(missing_pip)}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

        console.print("[bold green]Fixes attempted. Activate your venv and run doctor again.[/bold green]")

    elif not pydantic_ok:
        console.print("\n[bold red]Pydantic issue detected![/bold red]")
        console.print("Fix: [bold cyan]./setup.sh[/bold cyan] then [bold cyan]source .venv/bin/activate[/bold cyan]")
    elif missing_pip or missing_tools or not db_ok or not redis_ok:
        console.print("\n[bold red]Issues detected![/bold red] Run [bold]darkwin doctor --fix[/bold] or install missing components manually.")
    else:
        console.print("\n[bold green]✅ System is healthy! All components ready.[/bold green]")
