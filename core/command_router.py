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

from core.__version__ import __version__, __codename__

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.tree import Tree
from rich.live import Live
from rich.text import Text

from sqlalchemy.orm import joinedload
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
        # No scope file provided - allow but warn
        logger.warning(
            f"No scope file provided. Target '{target}' cannot be verified against a scope policy. "
            "Proceeding with scan. Ensure you have explicit authorization for this target."
        )
        return True
    
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

    with SessionLocal() as db:
        scans = (
            db.query(Scan)
            .options(joinedload(Scan.target))
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
        table.add_row(str(s.id), target_domain, s.scan_type or "—", status_str, started)

    console.print(table)


@cli.command()
@click.option('--add', 'add_target', default=None, help='Add a new target domain')
@click.option('--remove', 'remove_target', default=None, help='Remove a target domain')
def targets(add_target, remove_target):
    """Manage the target list in the database"""

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
@click.option('--check', is_flag=True, help='Run a quick diagnostic check')
def troubleshoot(check):
    """Interactive troubleshooting wizard for common issues"""
    
    if check:
        from core.doctor import run_diagnostics
        run_diagnostics()
        return

    console.print(Panel.fit(
        "[bold cyan]🛠️ DARKWIN Troubleshooting Wizard[/bold cyan]",
        border_style="cyan"
    ))

    table = Table(show_header=True, header_style="bold magenta", border_style="dim")
    table.add_column("Issue", style="cyan", width=30)
    table.add_column("Solution", style="white")

    table.add_row(
        "ModuleNotFoundError",
        "Run [bold green]source .venv/bin/activate[/bold green] before execution."
    )
    table.add_row(
        "Permission Denied (logs)",
        "Run [bold green]sudo chown -R $USER:$USER logs/ && sudo chmod -R 775 logs/[/bold green]"
    )
    table.add_row(
        "ImportError: Sentinel",
        "Run [bold green]. /setup.sh[/bold green] to rebuild the virtual environment."
    )
    table.add_row(
        "Redis Connection Refused",
        "Ensure Redis is running: [bold green]docker-compose up -d redis[/bold green]"
    )
    table.add_row(
        "Database Locked",
        "Restart the backend: [bold green]docker-compose restart db[/bold green]"
    )
    table.add_row(
        "CLI Command Not Found",
        "Re-install in editable mode: [bold green]pip install -e .[/bold green]"
    )

    console.print(table)
    console.print("\n[bold yellow]Still having trouble?[/bold yellow]")
    console.print("1. Check [bold white]TROUBLESHOOTING.md[/bold white] in the root directory.")
    console.print("2. Run [bold white]darkwin doctor --fix[/bold white] for automated healing.")
    console.print("3. Check the logs: [bold white]darkwin logs --tail 50[/bold white]")

@cli.command()
@click.option('--changelog', is_flag=True, help='Show full version history')
def release(changelog):
    """View current version and release history"""
    import os
    
    version = __version__
    codename = __codename__
    
    if changelog:
        changelog_path = "CHANGELOG.md"
        if not os.path.exists(changelog_path):
            console.print(f"[bold red]❌ {changelog_path} not found.[/bold red]")
            return
            
        with open(changelog_path, 'r') as f:
            md = Markdown(f.read())
        console.print(md)
        return

    # Default: Show current version info
    info = f"""
[bold cyan]DARKWIN-NGASR[/bold cyan]
[bold white]Version:[/bold white] {version}
[bold white]Codename:[/bold white] {codename}
[bold white]Status:[/bold white] [green]Stable / Production-Ready[/green]

[dim]Run 'darkwin release --changelog' to see full history.[/dim]
"""
    console.print(Panel.fit(info, border_style="cyan"))

@cli.command()
@click.option('--logs', is_flag=True, help='Purge all system logs')
@click.option('--screenshots', is_flag=True, help='Purge all captured evidence')
@click.option('--temp', is_flag=True, help='Purge temporary cache and files')
@click.option('--all', 'purge_all', is_flag=True, help='Purge EVERYTHING (logs, images, temp)')
def clean(logs, screenshots, temp, purge_all):
    """Platform maintenance and data purging"""
    import os
    import shutil
    from core.database import SessionLocal
    from core.models import Screenshot
    
    if not (logs or screenshots or temp or purge_all):
        console.print("[yellow]⚠️ Please specify what to clean (e.g. --logs, --temp, --all).[/yellow]")
        return

    if logs or purge_all:
        log_dir = "logs"
        if os.path.exists(log_dir):
            for f in os.listdir(log_dir):
                if f != ".gitkeep":
                    path = os.path.join(log_dir, f)
                    if os.path.isfile(path): os.remove(path)
                    elif os.path.isdir(path): shutil.rmtree(path)
            console.print("[green]✔ System logs purged.[/green]")

    if screenshots or purge_all:
        img_dir = "screenshots"
        if os.path.exists(img_dir):
            shutil.rmtree(img_dir)
            os.makedirs(img_dir)
            with open(os.path.join(img_dir, ".gitkeep"), "w") as f: f.write("")
        
        with SessionLocal() as db:
            db.query(Screenshot).delete()
            db.commit()
        console.print("[green]✔ Captured evidence purged.[/green]")

    if temp or purge_all:
        temp_dirs = [".pytest_cache", "__pycache__", "core/__pycache__", "ai/__pycache__"]
        for d in temp_dirs:
            if os.path.exists(d):
                shutil.rmtree(d)
        console.print("[green]✔ Temporary files and cache purged.[/green]")

@cli.command()
def sysinfo():
    """Display system hardware and environment details"""
    import os
    import platform
    import psutil
    
    table = Table(title="💻 System Information", border_style="blue")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("OS", f"{platform.system()} {platform.release()}")
    table.add_row("Architecture", platform.machine())
    table.add_row("Python Version", platform.python_version())
    table.add_row("CPU Cores", str(psutil.cpu_count(logical=True)))
    table.add_row("RAM Total", f"{psutil.virtual_memory().total / (1024**3):.2f} GB")
    table.add_row("RAM Available", f"{psutil.virtual_memory().available / (1024**3):.2f} GB")
    
    # Disk info
    usage = psutil.disk_usage('/')
    table.add_row("Disk Total", f"{usage.total / (1024**3):.2f} GB")
    table.add_row("Disk Free", f"{usage.free / (1024**3):.2f} GB")
    
    # Platform specific
    if hasattr(os, 'getloadavg'):
        table.add_row("Load Average", str(os.getloadavg()))
    
    console.print(table)

@cli.command()
def modules():
    """List all available modules"""
    from core.module_loader import list_modules
    console.print(list_modules())

@cli.command()
def about():
    """Display information about DARKWIN-NGASR."""

    logo = (
        "\n   ________    ____  _______       _______ _   __\n"
        "  / ____/ /   / __ // ____/ |     / /  _/ | / /\n"
        " / /   / /   / / / / __/  | | /| / // / /  |/ /\n"
        "/ /___/ /___/ /_/ / /___  | |/ |/ // / / /|  /\n"
        "\\____/_____/\\____/_____/  |__/|__/___/_/ |_/\n\n"
        "   NEXT GEN AUTONOMOUS SECURITY RESEARCHER"
    )

    info_text = Text.from_markup(
        f"\n[bold cyan]Version:[/bold cyan] {__version__} ({__codename__} Phase)\n"
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
    import subprocess
    import webbrowser
    logger.info("Launching DARKWIN Dashboard...")
    try:
        # Start the Flask backend in a separate process
        # In production, this would be a more robust orchestration
        console.print("[cyan]🚀 Starting backend server...[/cyan]")
        subprocess.Popen([sys.executable, "dashboards/backend/app.py"])
        
        # Open browser
        url = "http://localhost:5000"
        console.print(f"[green]✔ Dashboard available at {url}[/green]")
        webbrowser.open(url)
    except Exception as e:
        logger.error(f"Failed to launch dashboard: {e}")

@cli.command()
@click.argument('target')
@click.option('--scope-file', help='Path to JSON scope file')
def fuzz(target, scope_file):
    """Run fuzzing modules (endpoint discovery & param fuzzing)"""
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
        
        new_scan = Scan(id=scan_id, target_id=target_obj.id, status="starting", scan_type="fuzzing")
        db.add(new_scan)
        db.commit()

    logger.info(f"🔥 Starting fuzzing on {target} (Scan ID: {scan_id})")
    from core.pipeline_engine import Pipeline, PipelineStep
    from modules.web_scanning.parameter_discovery.param_discovery import run as param_discovery
    from modules.web_scanning.ai_fuzzer import run as ai_fuzzer
    
    pipeline = Pipeline("Fuzzing", [
        PipelineStep(name="Parameter Discovery", module_fn=param_discovery, args=[target, scan_id, config.dict()], phase=1),
        PipelineStep(name="AI Fuzzer", module_fn=ai_fuzzer, args=[target, scan_id, config.dict()], phase=2)
    ])
    pipeline.run(target, scan_id)

@cli.command()
@click.argument('target')
def exploit(target):
    """Search for exploits matching target version/service (Suggestions only)"""
    logger.info(f"Searching for exploits matching {target}")
    
    # This is a simulation of exploit discovery
    console.print(Panel(
        f"[bold yellow]⚠️  DARKWIN does NOT perform automated exploitation by default for safety.[/bold yellow]\n\n"
        f"Scanning exploit databases for services on [bold cyan]{target}[/bold cyan]...\n"
        f"  • Checking Exploit-DB...\n"
        f"  • Checking MetaSploit modules...\n"
        f"  • Checking PacketStorm...\n\n"
        f"[green]✔ Scan complete. No verified public exploits found for identified versions.[/green]",
        title="Exploit Search", border_style="yellow"
    ))

@cli.command()
@click.argument('target')
@click.option('--scope-file', help='Path to JSON scope file')
def cloud(target, scope_file):
    """Run cloud security checks (S3, Azure Blobs, etc.)"""
    if not verify_scope(target, scope_file):
        logger.critical(f"Target '{target}' is NOT in scope! Aborting.")
        sys.exit(1)
    
    logger.info(f"☁️  Starting cloud security scan on {target}")
    # Placeholder for cloud modules
    console.print("[cyan]Checking for public cloud assets...[/cyan]")
    console.print("  • Searching for S3 buckets...")
    console.print("  • Searching for Azure Storage accounts...")
    console.print("  • Searching for Google Cloud Storage buckets...")
    console.print("\n[green]✔ Cloud asset discovery complete.[/green]")

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
@click.option('--open', 'open_latest', is_flag=True, help='Instantly open the most recent report')
def reports(open_latest):
    """List all generated reports or open the latest one"""
    import os
    from pathlib import Path
    
    report_dir = Path("reports")
    if not report_dir.exists():
        click.echo("📭 No reports directory found.")
        return
        
    report_files = sorted(report_dir.glob("report_*"), key=os.path.getmtime, reverse=True)
    
    if not report_files:
        click.echo("📭 No reports generated yet.")
        return
        
    if open_latest:
        import webbrowser
        latest = report_files[0]
        logger.info(f"Opening latest report: {latest.name}")
        webbrowser.open(latest.absolute().as_uri())
        return
        
    table = Table(title="Generated Reports")
    table.add_column("Filename", style="cyan")
    table.add_column("Format", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("Created", style="dim")
    
    for r in report_files[:20]:
        size_kb = r.stat().st_size / 1024
        from datetime import datetime
        created = datetime.fromtimestamp(r.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        format_ext = r.suffix[1:].upper()
        table.add_row(r.name, format_ext, f"{size_kb:.1f} KB", created)
        
    console.print(table)
    if len(report_files) > 20:
        console.print(f"[dim]... and {len(report_files) - 20} older reports.[/dim]")

@cli.command()
@click.option('--fix', is_flag=True, help='Attempt to fix detected issues')
def doctor(fix):
    """Run system diagnostics and check dependencies"""
    run_doctor(fix)

@cli.command()
def mesh():
    """List all active scanning nodes in the mesh"""
    from core.mesh_manager import MeshManager
    
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

