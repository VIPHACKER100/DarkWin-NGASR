import click
import json
import os
import sys
from rich.console import Console
from core.config_manager import validate_config, get_config
from core.logging_system import get_logger

console = Console()
logger = get_logger("CLI")

def verify_scope(target: str, scope_file: str = None) -> bool:
    """
    Verify if the target is within the authorized scope.
    """
    if not scope_file:
        # If no scope file, we require manual confirmation or assume out-of-scope for now
        # In a real tool, we might check a database or default allowed list
        return False
    
    try:
        if not os.path.exists(scope_file):
            logger.error(f"Scope file not found: {scope_file}")
            return False
            
        with open(scope_file, 'r') as f:
            scope_data = json.load(f)
            authorized_domains = scope_data.get("authorized_domains", [])
            authorized_ips = scope_data.get("authorized_ips", [])
            
            if target in authorized_domains or target in authorized_ips:
                return True
                
            # Basic wildcard check (e.g., example.com matches *.example.com)
            for domain in authorized_domains:
                if domain.startswith("*."):
                    base_domain = domain[2:]
                    if target == base_domain or target.endswith("." + base_domain):
                        return True
        
        return False
    except Exception as e:
        logger.error(f"Error reading scope file: {e}")
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
    logger.info(f"Starting reconnaissance on {target}")
    # Implementation will call pipeline_engine later

@cli.command()
@click.argument('target')
@click.option('--scope-file', help='Path to JSON scope file')
def scan(target, scope_file):
    """Run vulnerability scan pipeline"""
    if not verify_scope(target, scope_file):
        logger.critical(f"Target '{target}' is NOT in scope! Aborting.")
        sys.exit(1)
    logger.info(f"Starting vulnerability scan on {target}")

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
