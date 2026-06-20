"""DARKWIN Setup Wizard

Provides an interactive CLI interface for configuring DARKWIN settings,
API keys, and service connections.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import os
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from core.config_manager import get_config, DarkwinConfig

console: Console = Console()

def run_setup_wizard() -> None:
    """Run interactive setup wizard to configure config.yaml."""
    console.print(Panel.fit(
        "[bold cyan]DARKWIN Configuration Wizard[/bold cyan]\n"
        "This wizard will help you set up your API keys and service connections.",
        title="Welcome"
    ))
    
    config = get_config()
    
    # 1. Database Configuration
    console.print("\n[bold]1. Database Configuration[/bold]")
    db_url = Prompt.ask("Database URL", default=config.database.url)
    config.database.url = db_url
    
    # 2. Redis Configuration
    console.print("\n[bold]2. Redis Configuration[/bold]")
    redis_url = Prompt.ask("Redis URL", default=config.redis.url)
    config.redis.url = redis_url
    
    # 3. API Keys
    console.print("\n[bold]3. External API Keys[/bold]")
    shodan_key = Prompt.ask("Shodan API Key", default=config.api_keys.shodan, password=True)
    config.api_keys.shodan = shodan_key
    
    github_token = Prompt.ask("GitHub Personal Access Token", default=config.api_keys.github_token, password=True)
    config.api_keys.github_token = github_token
    
    openai_key = Prompt.ask("OpenAI API Key", default=config.ai.openai_api_key, password=True)
    config.ai.openai_api_key = openai_key
    
    # 4. AI Settings
    console.print("\n[bold]4. AI Settings[/bold]")
    config.ai.openai_model = Prompt.ask("OpenAI Model", default=config.ai.openai_model)
    
    # Save Configuration
    console.print("\n" + Panel.fit("[bold green]Setup Complete![/bold green]"))
    if Confirm.ask("Save configuration to config.yaml?"):
        save_path = "config.yaml"
        # Convert Pydantic model to dict for YAML
        # Note: We use dict() for Pydantic v1, model_dump() for Pydantic v2
        config_dict = config.model_dump() if hasattr(config, "model_dump") else config.dict()
        
        Path(save_path).write_text(yaml.dump(config_dict, default_flow_style=False))
        
        console.print(f"[bold green]Configuration saved successfully to {save_path}[/bold green]")
    else:
        console.print("[bold yellow]Changes discarded.[/bold yellow]")

if __name__ == "__main__":
    run_setup_wizard()
