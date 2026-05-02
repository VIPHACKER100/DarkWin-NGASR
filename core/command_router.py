"""DARKWIN CLI Command Router

Provides click-based CLI interface for security scanning operations.
Includes scope verification, pipeline orchestration, and module management.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import click
from rich.console import Console

from core.config_manager import validate_config, get_config
from core.logging_system import get_logger
from core.database import SessionLocal
from core.models import Target, Scan
from pipelines.recon_pipeline import get_recon_pipeline
from pipelines.web_vuln_pipeline import get_web_vuln_pipeline
from pipelines.full_hunt_pipeline import get_full_hunt_pipeline
from core.doctor import run_doctor
from core.setup_wizard import run_setup_wizard

console: Console = Console()
logger = get_logger("CLI")

def verify_scope(target: str, scope_file: Optional[str] = None) -> bool:
    """Verify if the target is within authorized scope.
    
    Checks target against authorized domains and IPs from scope file.
    Supports wildcard domain matching (e.g., *.example.com).
    
    Args:
        target: Target domain or IP address to verify.
        scope_file: Optional path to JSON scope file with authorized targets.
    
    Returns:
        True if target is in scope, False otherwise.
    
    Raises:
        None (logs errors instead of raising).
    """
    if not scope_file:
        # No scope file provided - require explicit authorization
        logger.warning(
            f"No scope file provided. Target '{target}' cannot be verified. "
            "Skipping scope check (provide --scope-file for verification)."
        )
        return False
    
    scope_path = Path(scope_file)
    
    if not scope_path.exists():
        logger.error(f"Scope file not found: {scope_file}")
        return False
    
    try:
        scope_data: Dict[str, Any] = json.loads(scope_path.read_text())
        authorized_domains: list = scope_data.get("authorized_domains", [])
        authorized_ips: list = scope_data.get("authorized_ips", [])
        
        # Direct match
        if target in authorized_domains or target in authorized_ips:
            return True
        
        # Wildcard domain matching (e.g., *.example.com matches sub.example.com)
        for domain in authorized_domains:
            if domain.startswith("*."):
                base_domain: str = domain[2:]
                if target == base_domain or target.endswith("." + base_domain):
                    return True
        
        return False
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in scope file: {e}")
        return False
    except Exception as e:
        logger.error(f"Error reading scope file: {e}", exc_info=True)
        return False

@click.group()
def cli():
    """DARKWIN — Next-Generation Automated Security Research Platform"""
    pass

@cli.command()
@click.argument('target')
@click.option('--scope-file', help='Path to JSON scope file')
def recon(target, scope_file):
    """Run reconnaissance pipeline"""
    if not verify_scope(target, scope_file):
        logger.critical(f"Target '{target}' is NOT in scope! Aborting.")
        sys.exit(1)
    
    config = get_config()
    scan_id = str(uuid.uuid4())
    
    with SessionLocal() as db:
        # Ensure target exists
        target_obj = db.query(Target).filter(Target.domain == target).first()
        if not target_obj:
            target_obj = Target(domain=target, scope_confirmed=True)
            db.add(target_obj)
            db.commit()
            db.refresh(target_obj)
            
        # Create scan entry
        new_scan = Scan(id=scan_id, target_id=target_obj.id, status="starting")
        db.add(new_scan)
        db.commit()

    logger.info(f"Starting reconnaissance on {target} (Scan ID: {scan_id})")
    pipeline = get_recon_pipeline(target, scan_id, config.dict())
    pipeline.run(target, scan_id)

@cli.command()
@click.argument('target')
@click.option('--scope-file', help='Path to JSON scope file')
def scan(target, scope_file):
    """Run vulnerability scan pipeline"""
    if not verify_scope(target, scope_file):
        logger.critical(f"Target '{target}' is NOT in scope! Aborting.")
        sys.exit(1)
    
    config = get_config()
    scan_id = str(uuid.uuid4())
    
    with SessionLocal() as db:
        target_obj = db.query(Target).filter(Target.domain == target).first()
        if not target_obj:
            target_obj = Target(domain=target, scope_confirmed=True)
            db.add(target_obj)
            db.commit()
            db.refresh(target_obj)
            
        new_scan = Scan(id=scan_id, target_id=target_obj.id, status="starting")
        db.add(new_scan)
        db.commit()

    logger.info(f"Starting vulnerability scan on {target} (Scan ID: {scan_id})")
    pipeline = get_web_vuln_pipeline(target, scan_id, config.dict())
    pipeline.run(target, scan_id)

@cli.command()
@click.argument('target')
@click.option('--scope-file', help='Path to JSON scope file')
@click.option('--max-steps', default=5, help='Maximum reasoning steps')
def hunt(target, scope_file, max_steps):
    """Full autonomous bug bounty hunt using AI reasoning"""
    if not verify_scope(target, scope_file):
        logger.critical(f"Target '{target}' is NOT in scope! Aborting.")
        sys.exit(1)
    
    from core.agent_loop import AgenticLoop
    import asyncio
    
    scan_id = str(uuid.uuid4())
    
    with SessionLocal() as db:
        target_obj = db.query(Target).filter(Target.domain == target).first()
        if not target_obj:
            target_obj = Target(domain=target, scope_confirmed=True)
            db.add(target_obj)
            db.commit()
            db.refresh(target_obj)
            
        new_scan = Scan(id=scan_id, target_id=target_obj.id, status="starting", scan_type="autonomous")
        db.add(new_scan)
        db.commit()

    logger.info(f"🚀 Starting autonomous hunt on {target} (Scan ID: {scan_id})")
    loop = AgenticLoop(target, scan_id, max_steps=max_steps)
    asyncio.run(loop.run())

@cli.command()
def modules():
    """List all available modules"""
    from core.module_loader import list_all_modules
    list_all_modules()

@cli.command()
def about():
    """Display information about DARKWIN-NGASR."""
    from rich.panel import Panel
    from rich.text import Text

    logo = (
        "\n   ________    ____  _______       _______ _   __\n"
        "  / ____/ /   / __ // ____/ |     / /  _/ | / /\n"
        " / /   / /   / / / / __/  | | /| / // / /  |/ /\n"
        "/ /___/ /___/ /_/ / /___  | |/ |/ // / / /|  /\n"
        "\\____/_____/\\____/_____/  |__/|__/___/_/ |_/\n\n"
        "   NEXT GEN AUTONOMOUS SECURITY RESEARCHER"
    )

    info_text = Text.from_markup(
        "\n[bold cyan]Version:[/bold cyan] 1.0.0 (Zenith Phase)\n"
        "[bold cyan]Author:[/bold cyan] ARYAN AHIRWAR (VIPHACKER.100)\n"
        "[bold cyan]Status:[/bold cyan] Production Ready\n\n"
        "[italic white]An autonomous, distributed, and stealthy ecosystem for\n"
        "proactive security reconnaissance and vulnerability intelligence.[/italic white]\n\n"
        "Use [bold]darkwin update[/bold] to keep your ecosystem synchronized."
    )

    console.print(Panel(Text(logo, style="bold magenta"), border_style="magenta"))
    console.print(Panel(info_text, border_style="cyan", title="Project Status"))

@cli.command()
def dashboard():
    """Launch web dashboard"""
    logger.info("Launching DARKWIN Dashboard...")
    # Will start the Flask app

@cli.command()
@click.argument('target')
@click.option('--scope-file', help='Path to JSON scope file')
def fuzz(target, scope_file):
    """Run fuzzing modules"""
    if not verify_scope(target, scope_file):
        logger.critical(f"Target '{target}' is NOT in scope! Aborting.")
        sys.exit(1)
    logger.info(f"Starting fuzzing on {target}")

@cli.command()
@click.argument('target')
def exploit(target):
    """Search for exploits (suggestions only)"""
    logger.info(f"Searching for exploits matching {target}")

@cli.command()
@click.argument('target')
@click.option('--scope-file', help='Path to JSON scope file')
def cloud(target, scope_file):
    """Run cloud security checks"""
    if not verify_scope(target, scope_file):
        logger.critical(f"Target '{target}' is NOT in scope! Aborting.")
        sys.exit(1)
    logger.info(f"Starting cloud security scan on {target}")

@cli.command()
@click.argument('target')
def watch(target):
    """Continuous monitoring"""
    logger.info(f"Starting continuous monitoring on {target}")
    from automation.auto_bug_hunter.hunter import watch_target
    watch_target(target)

@cli.command()
@click.argument('scan_id')
@click.option('--format', type=click.Choice(['md', 'html', 'pdf']), default='md', help='Report format')
def report(scan_id, format):
    """Generate a comprehensive security report for a scan"""
    from core.reporting_engine import ReportingEngine
    
    try:
        engine = ReportingEngine()
        filepath = engine.generate_report(scan_id, format=format)
        click.echo(f"✅ Report generated successfully: {filepath}")
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        click.echo(f"❌ Error: {str(e)}")

@cli.command()
@click.option('--fix', is_flag=True, help='Attempt to fix detected issues')
def doctor(fix):
    """Run system diagnostics and check dependencies"""
    run_doctor(fix)

@cli.command()
def mesh():
    """List all active scanning nodes in the mesh"""
    from core.mesh_manager import MeshManager
    from rich.table import Table
    
    manager = MeshManager()
    nodes = manager.list_nodes()
    
    if not nodes:
        click.echo("📭 No active nodes found in the mesh.")
        return
        
    table = Table(title="DARKWIN Mesh Nodes")
    table.add_column("Node ID", style="cyan")
    table.add_column("Hostname", style="green")
    table.add_column("OS", style="white")
    table.add_column("Last Seen (UTC)", style="dim")
    
    for node in nodes:
        table.add_row(
            node["id"],
            node["hostname"],
            node["os"],
            node.get("last_seen", "Unknown")
        )
        
    console.print(table)

@cli.command()
def proxy():
    """List available proxies in the rotation pool"""
    from core.proxy_manager import global_proxy_manager
    proxies = global_proxy_manager.get_proxy_list()
    if not proxies:
        click.echo("📭 No proxies configured in the pool.")
        return
    click.echo(f"🌐 Found {len(proxies)} proxies in pool:")
    for p in proxies:
        click.echo(f" - {p}")

@cli.command()
def test():
    """Run core unit tests"""
    from core.tests.test_core import run_tests
    console.print("[bold cyan]🧪 Running DARKWIN Core Tests...[/bold cyan]")
    run_tests()

@cli.command()
def update_templates():
    """Update Nuclei vulnerability templates"""
    import subprocess
    from core.config_manager import get_config
    config = get_config()
    nuclei_bin = config.tools.nuclei
    
    console.print(f"[bold cyan]🔄 Updating {nuclei_bin} templates...[/bold cyan]")
    try:
        subprocess.run([nuclei_bin, "-ut"], check=True)
        console.print("[bold green]✨ Templates updated successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Template update failed: {e}[/bold red]")

@cli.command()
def update():
    """Pull latest changes and update the ecosystem"""
    import subprocess
    console.print("[bold cyan]🔄 Updating DARKWIN-NGASR...[/bold cyan]")
    
    try:
        # 1. Git Pull
        console.print("📥 Fetching latest changes from GitHub...")
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        
        # 2. Run Setup
        console.print("🛠️ Running environment setup...")
        if sys.platform == "win32":
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "./setup.ps1"], check=False)
        else:
            subprocess.run(["bash", "./setup.sh"], check=True)
            
        console.print("[bold green]✨ DARKWIN updated successfully![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Update failed: {e}[/bold red]")

@cli.command()
def shell():
    """Launch interactive DARKWIN shell"""
    import asyncio
    from core.interactive_shell import DarkWinShell
    s = DarkWinShell()
    asyncio.run(s.start())

@cli.command()
def setup():
    """Run interactive configuration wizard"""
    run_setup_wizard()

