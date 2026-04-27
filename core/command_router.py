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
def hunt(target, scope_file):
    """Full bug bounty pipeline"""
    if not verify_scope(target, scope_file):
        logger.critical(f"Target '{target}' is NOT in scope! Aborting.")
        sys.exit(1)
    logger.info(f"Starting bug bounty hunt on {target}")

@cli.command()
def modules():
    """List all available modules"""
    from core.module_loader import list_all_modules
    list_all_modules()

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
def report(scan_id):
    """Generate reports"""
    logger.info(f"Generating reports for Scan ID: {scan_id}")

