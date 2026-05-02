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
@click.option('--limit', default=20, help='Number of recent scans to show')
def history(limit):
    """View recent scan history from the database"""
    from rich.table import Table

    with SessionLocal() as db:
        scans = (
            db.query(Scan)
            .order_by(Scan.started_at.desc())
            .limit(limit)
            .all()
        )

    if not scans:
        console.print("[yellow]No scan history found.[/yellow]")
        return

    table = Table(title=f"📋 Scan History (last {limit})", border_style="cyan")
    table.add_column("Scan ID", style="dim", max_width=18)
    table.add_column("Target", style="bold white")
    table.add_column("Type", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Started", style="dim")

    status_colors = {
        "completed": "[green]completed[/green]",
        "running":   "[bold cyan]running[/bold cyan]",
        "failed":    "[red]failed[/red]",
        "starting":  "[yellow]starting[/yellow]",
    }

    for s in scans:
        target_domain = s.target.domain if s.target else "unknown"
        started = s.started_at.strftime("%Y-%m-%d %H:%M") if s.started_at else "—"
        status_str = status_colors.get(s.status, s.status)
        table.add_row(str(s.id)[:16] + "..", target_domain, s.scan_type or "—", status_str, started)

    console.print(table)


@cli.command()
@click.option('--add', 'add_target', default=None, help='Add a new target domain')
@click.option('--remove', 'remove_target', default=None, help='Remove a target domain')
def targets(add_target, remove_target):
    """Manage the target list in the database"""
    from rich.table import Table

    with SessionLocal() as db:
        if add_target:
            existing = db.query(Target).filter(Target.domain == add_target).first()
            if existing:
                console.print(f"[yellow]Target '{add_target}' already exists.[/yellow]")
            else:
                db.add(Target(domain=add_target, scope_confirmed=True))
                db.commit()
                console.print(f"[green]✅ Target '{add_target}' added.[/green]")
            return

        if remove_target:
            t = db.query(Target).filter(Target.domain == remove_target).first()
            if t:
                db.delete(t)
                db.commit()
                console.print(f"[green]✅ Target '{remove_target}' removed.[/green]")
            else:
                console.print(f"[red]Target '{remove_target}' not found.[/red]")
            return

        # Default: list all targets
        all_targets = db.query(Target).order_by(Target.created_at.desc()).all()

    if not all_targets:
        console.print("[yellow]No targets found. Use --add <domain> to add one.[/yellow]")
        return

    table = Table(title="🎯 Target Scope List", border_style="magenta")
    table.add_column("ID", style="dim")
    table.add_column("Domain", style="bold white")
    table.add_column("Scope", justify="center")
    table.add_column("Scans", justify="right")
    table.add_column("Added", style="dim")

    for t in all_targets:
        scope = "[green]✔ Confirmed[/green]" if t.scope_confirmed else "[red]✖ Not Confirmed[/red]"
        table.add_row(
            str(t.id),
            t.domain,
            scope,
            str(len(t.scans)),
            t.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)


@cli.command()
@click.option('--download', is_flag=True, help='Download recommended wordlists')
def wordlists(download):
    """View and manage local security wordlists"""
    import os
    import requests
    from rich.table import Table
    
    wordlists_dir = "wordlists"
    os.makedirs(wordlists_dir, exist_ok=True)
    
    recommended = {
        "subdomains.txt": "https://raw.githubusercontent.com/rbsec/dnscan/master/subdomains-10000.txt",
        "directories.txt": "https://raw.githubusercontent.com/maurosoria/dirsearch/master/db/dicc.txt",
        "parameters.txt": "https://raw.githubusercontent.com/projectdiscovery/fuzz-bores/main/wordlists/parameters.txt"
    }
    
    if download:
        console.print("[bold cyan]📥 Downloading recommended wordlists...[/bold cyan]")
        for name, url in recommended.items():
            path = os.path.join(wordlists_dir, name)
            if os.path.exists(path):
                console.print(f"  [yellow]![/yellow] {name} already exists. Skipping.")
                continue
            try:
                console.print(f"  [blue]→[/blue] Downloading {name}...")
                r = requests.get(url, timeout=30)
                with open(path, "wb") as f:
                    f.write(r.content)
                console.print(f"  [green]✔[/green] {name} saved.")
            except Exception as e:
                console.print(f"  [red]✘[/red] Failed to download {name}: {e}")
        return

    # List local wordlists
    files = [f for f in os.listdir(wordlists_dir) if os.path.isfile(os.path.join(wordlists_dir, f))]
    
    table = Table(title="📁 Local Wordlists", border_style="cyan")
    table.add_column("Filename", style="bold white")
    table.add_column("Size", justify="right")
    table.add_column("Status", justify="center")
    
    for name in recommended.keys():
        path = os.path.join(wordlists_dir, name)
        exists = os.path.exists(path)
        size = f"{os.path.getsize(path) / 1024:.1f} KB" if exists else "—"
        status = "[green]Ready[/green]" if exists else "[red]Missing[/red]"
        table.add_row(name, size, status)
        
    for f in files:
        if f not in recommended:
            path = os.path.join(wordlists_dir, f)
            size = f"{os.path.getsize(path) / 1024:.1f} KB"
            table.add_row(f, size, "[white]Custom[/white]")
            
    console.print(table)
    if not any(os.path.exists(os.path.join(wordlists_dir, n)) for n in recommended.keys()):
        console.print("\n[yellow]💡 Tip: Run 'darkwin wordlists --download' to get started.[/yellow]")

@cli.command()
@click.option('--type', 'payload_type', help='Filter payloads by type (xss, sqli, lfi, etc.)')
def payloads(payload_type):
    """View and manage exploit payloads"""
    import os
    from rich.table import Table
    from rich.tree import Tree
    
    payloads_dir = "payloads"
    os.makedirs(payloads_dir, exist_ok=True)
    
    # Categorized payloads (Examples)
    categories = {
        "xss": ["<script>alert(1)</script>", "javascript:alert(1)", "<img src=x onerror=alert(1)>"],
        "sqli": ["' OR '1'='1", "' UNION SELECT NULL--", "admin'--"],
        "lfi": ["../../../../etc/passwd", "..\\..\\..\\..\\windows\\win.ini", "/etc/hosts"],
        "rce": ["; id", "`id`", "| id", "$(id)"]
    }
    
    # Ensure local files exist for these categories if not already present
    for cat, items in categories.items():
        cat_dir = os.path.join(payloads_dir, cat)
        os.makedirs(cat_dir, exist_ok=True)
        default_file = os.path.join(cat_dir, "default.txt")
        if not os.path.exists(default_file):
            with open(default_file, "w") as f:
                f.write("\n".join(items))

    if payload_type:
        cat_path = os.path.join(payloads_dir, payload_type)
        if not os.path.exists(cat_path):
            console.print(f"[bold red]✘ Category '{payload_type}' not found.[/bold red]")
            return
        
        table = Table(title=f"🔥 {payload_type.upper()} Payloads", border_style="red")
        table.add_column("Payload", style="bold white")
        
        for root, _, files in os.walk(cat_path):
            for file in files:
                with open(os.path.join(root, file), "r") as f:
                    for line in f.readlines():
                        if line.strip():
                            table.add_row(line.strip())
        console.print(table)
        return

    # Tree view of all payloads
    tree = Tree("📂 [bold]Payloads Repository[/bold]", guide_style="bold red")
    
    for cat in os.listdir(payloads_dir):
        cat_path = os.path.join(payloads_dir, cat)
        if os.path.isdir(cat_path):
            cat_node = tree.add(f"[bold yellow]{cat.upper()}[/bold yellow]")
            for file in os.listdir(cat_path):
                file_path = os.path.join(cat_path, file)
                if os.path.isfile(file_path):
                    count = sum(1 for line in open(file_path) if line.strip())
                    cat_node.add(f"{file} ([dim]{count} payloads[/dim])")
    
    console.print(tree)
    console.print("\n[yellow]💡 Tip: Use 'darkwin payloads --type <name>' to view specific strings.[/yellow]")

@cli.command()
@click.option('--scan-id', help='Filter screenshots by Scan ID')
@click.option('--open', 'open_img', is_flag=True, help='Open the latest screenshot')
def screenshots(scan_id, open_img):
    """View and manage captured evidence screenshots"""
    import os
    import subprocess
    from rich.table import Table
    from core.database import SessionLocal
    from core.models import Screenshot
    
    with SessionLocal() as db:
        query = db.query(Screenshot)
        if scan_id:
            query = query.filter(Screenshot.scan_id == scan_id)
        
        results = query.order_by(Screenshot.created_at.desc()).all()

    if not results:
        console.print("[yellow]No screenshots found in the database.[/yellow]")
        return

    if open_img:
        latest = results[0]
        console.print(f"[bold cyan]🖼️ Opening latest screenshot: {latest.filename}[/bold cyan]")
        try:
            if os.name == 'nt':
                os.startfile(latest.filepath)
            else:
                subprocess.run(['xdg-open', latest.filepath], check=True)
        except Exception as e:
            console.print(f"[bold red]❌ Failed to open screenshot: {e}[/bold red]")
        return

    table = Table(title="📸 Captured Evidence", border_style="magenta")
    table.add_column("Scan ID", style="dim")
    table.add_column("Filename", style="bold white")
    table.add_column("URL", style="blue")
    table.add_column("Captured At", style="dim")
    
    for s in results:
        table.add_row(
            s.scan_id[:8] + "...",
            s.filename,
            s.url or "—",
            s.created_at.strftime("%Y-%m-%d %H:%M")
        )
    
    console.print(table)
    console.print(f"\n[bold green]Total Screenshots: {len(results)}[/bold green]")
    console.print("[yellow]💡 Tip: Use 'darkwin screenshots --open' to view the latest capture.[/yellow]")

@cli.command()
@click.option('--edit', is_flag=True, help='Open config.yaml in default editor')
@click.option('--view', is_flag=True, help='View current configuration (masked)')
def config(edit, view):
    """View or edit platform configuration"""
    import os
    import subprocess
    import yaml
    from rich.syntax import Syntax
    
    config_path = "config.yaml"
    
    if edit:
        console.print(f"[bold cyan]📝 Opening {config_path} for editing...[/bold cyan]")
        try:
            if os.name == 'nt':
                os.startfile(config_path)
            else:
                editor = os.environ.get('EDITOR', 'nano')
                subprocess.run([editor, config_path], check=True)
        except Exception as e:
            console.print(f"[bold red]❌ Failed to open editor: {e}[/bold red]")
        return

    if view:
        if not os.path.exists(config_path):
            console.print(f"[bold red]❌ {config_path} not found![/bold red]")
            return
            
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            
        # Mask sensitive keys
        def mask_recursive(d):
            if not isinstance(d, dict): return
            for k, v in d.items():
                if any(word in k.lower() for word in ['api_key', 'secret', 'password', 'token', 'webhook']):
                    d[k] = "********"
                elif isinstance(v, dict):
                    mask_recursive(v)
        
        mask_recursive(data)
        masked_yaml = yaml.dump(data, default_flow_style=False)
        
        syntax = Syntax(masked_yaml, "yaml", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"⚙️ {config_path} (Masked)", border_style="cyan"))
        return

    # Default: Show info
    console.print(f"[bold cyan]DARKWIN Configuration Management[/bold cyan]")
    console.print(f"Path: [bold]{os.path.abspath(config_path)}[/bold]")
    console.print("\nAvailable options:")
    console.print("  --view : View the current configuration with masked secrets")
    console.print("  --edit : Open the configuration file in your default editor")

@cli.command()
@click.option('--add', 'add_task', help='Schedule a new task (e.g. "hunt example.com weekly")')
@click.option('--list', 'list_tasks', is_flag=True, help='List all scheduled tasks')
@click.option('--remove', 'remove_id', help='Remove a scheduled task by ID')
def schedule(add_task, list_tasks, remove_id):
    """Manage periodic security scans and tasks"""
    import os
    import json
    from rich.table import Table
    
    schedule_file = "logs/schedule.json"
    os.makedirs("logs", exist_ok=True)
    
    def load_schedule():
        if os.path.exists(schedule_file):
            with open(schedule_file, "r") as f:
                return json.load(f)
        return []

    def save_schedule(tasks):
        with open(schedule_file, "w") as f:
            json.dump(tasks, f, indent=4)

    tasks = load_schedule()

    if add_task:
        import uuid
        from datetime import datetime
        parts = add_task.split()
        if len(parts) < 2:
            console.print("[bold red]❌ Invalid format. Use: 'hunt <target> <frequency>'[/bold red]")
            return
        
        new_task = {
            "id": str(uuid.uuid4())[:8],
            "command": parts[0],
            "target": parts[1],
            "frequency": parts[2] if len(parts) > 2 else "daily",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "active"
        }
        tasks.append(new_task)
        save_schedule(tasks)
        console.print(f"[bold green]✔ Task scheduled successfully (ID: {new_task['id']})[/bold green]")
        return

    if remove_id:
        new_tasks = [t for t in tasks if t['id'] != remove_id]
        if len(new_tasks) < len(tasks):
            save_schedule(new_tasks)
            console.print(f"[bold green]✔ Task {remove_id} removed.[/bold green]")
        else:
            console.print(f"[bold red]❌ Task {remove_id} not found.[/bold red]")
        return

    # List tasks
    table = Table(title="📅 Scheduled Tasks", border_style="yellow")
    table.add_column("ID", style="dim")
    table.add_column("Command", style="bold white")
    table.add_column("Target", style="cyan")
    table.add_column("Frequency", style="magenta")
    table.add_column("Created At", style="dim")
    
    for t in tasks:
        table.add_row(t['id'], t['command'], t['target'], t['frequency'], t['created_at'])
        
    console.print(table)
    console.print("\n[yellow]Note: Scheduling requires the Celery Beat worker to be running.[/yellow]")

@cli.command()
@click.option('--tail', default=20, help='Number of lines to show')
@click.option('--follow', is_flag=True, help='Follow log output in real-time')
@click.option('--search', help='Search logs for a specific keyword')
def logs(tail, follow, search):
    """View and search system logs"""
    import os
    import time
    from rich.live import Live
    
    log_file = "logs/darkwin.log"
    if not os.path.exists(log_file):
        console.print(f"[bold red]❌ Log file not found: {log_file}[/bold red]")
        return

    def get_lines(n):
        with open(log_file, "r") as f:
            lines = f.readlines()
            return lines[-n:]

    if search:
        console.print(f"[bold cyan]🔍 Searching logs for: '{search}'...[/bold cyan]")
        with open(log_file, "r") as f:
            count = 0
            for line in f:
                if search.lower() in line.lower():
                    console.print(line.strip())
                    count += 1
            console.print(f"\n[bold green]Found {count} matches.[/bold green]")
        return

    if follow:
        console.print(f"[bold cyan]👀 Tailing logs (Ctrl+C to stop):[/bold cyan]")
        try:
            with open(log_file, "r") as f:
                f.seek(0, 2)  # Go to end
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    console.print(line.strip())
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped tailing logs.[/yellow]")
        return

    # Default: Show tail
    lines = get_lines(tail)
    console.print(Panel("\n".join([l.strip() for l in lines]), title=f"📋 Last {tail} logs", border_style="dim"))

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

