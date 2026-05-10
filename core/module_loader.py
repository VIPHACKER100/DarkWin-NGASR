"""DARKWIN Dynamic Module Loader & Discovery

Provides runtime module discovery and loading for DARKWIN scanner modules.
Supports dynamic discovery of vulnerability scanners, fuzzing modules, and tools.

Exports:
    list_modules(): Discover and display all available modules
    get_module(name): Retrieve a module by name or import path
    
Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import importlib
import pkgutil
from pathlib import Path
from typing import Optional, Dict, Any, List

from rich.table import Table
from rich.console import Console

from core.logging_system import get_logger
from core.base_module import BaseModule

console: Console = Console()
logger = get_logger("ModuleLoader")

# Constants
MODULES_DIR: str = "modules"
MODULE_META_ATTR: str = "MODULE_META"

# Registry for fast lookup
_module_registry: Dict[str, Any] = {}
_registry_loaded: bool = False


def list_modules() -> Table:
    """Discover and display all available scanner modules.
    
    Walks the modules directory, discovers packages, and collects
    module metadata for display in a formatted table.
    
    Returns:
        Rich Table with module information (category, name, description, version).
    """
    table: Table = Table(title="DARKWIN Loaded Modules")
    table.add_column("Category", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    table.add_column("Version", style="dim")

    modules_path: str = str(Path.cwd() / MODULES_DIR)
    module_data: List[Dict[str, str]] = []

    try:
        # Walk through modules directory and discover packages
        for loader, module_name, is_pkg in pkgutil.walk_packages(
            [modules_path], prefix=f"{MODULES_DIR}."
        ):
            # Skip subpackages, only process actual modules
            if is_pkg:
                continue
            
            try:
                module = importlib.import_module(module_name)
                meta: Optional[Dict[str, Any]] = getattr(
                    module, MODULE_META_ATTR, None
                )
                
                if meta:
                    module_data.append({
                        "category": meta.get("category", "General"),
                        "name": meta.get("name", module_name),
                        "description": meta.get("description", "No description"),
                        "version": meta.get("version", "1.0.0")
                    })
                    
            except ImportError as e:
                logger.warning(f"Failed to import module {module_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error loading module {module_name}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error discovering modules: {e}", exc_info=True)
        table.add_row("[red]Error[/red]", "Failed to discover modules", str(e), "N/A")
        return table

    # Sort by category and add to table
    for module_info in sorted(module_data, key=lambda x: x["category"]):
        table.add_row(
            module_info["category"],
            module_info["name"],
            module_info["description"],
            module_info["version"]
        )

    return table


def get_module(name: str) -> Any:
    """Retrieve a module by metadata name or import path (with caching)."""
    
    # Check registry first
    if name in _module_registry:
        return _module_registry[name]
    
    # If not in registry and registry not loaded, load it
    if not _registry_loaded:
        _load_registry()
        if name in _module_registry:
            return _module_registry[name]

    # Fallback to direct import attempt if it looks like a path
    if name.startswith(f"{MODULES_DIR}."):
        try:
            module = importlib.import_module(name)
            _verify_module(module)
            _module_registry[name] = module
            return module
        except Exception as e:
            logger.error(f"Failed to load module by path '{name}': {e}")

    logger.error(f"Module not found: {name}")
    raise ModuleNotFoundError(f"Module '{name}' not found in DARKWIN library.")


def _load_registry():
    """Populate the module registry by scanning the modules directory."""
    global _registry_loaded
    logger.debug("Loading module registry...")
    
    modules_path: str = str(Path.cwd() / MODULES_DIR)
    
    try:
        for loader, module_name, is_pkg in pkgutil.walk_packages(
            [modules_path], prefix=f"{MODULES_DIR}."
        ):
            if is_pkg: continue
            
            try:
                module = importlib.import_module(module_name)
                meta = getattr(module, MODULE_META_ATTR, None)
                
                if meta:
                    meta_name = meta.get("name")
                    if meta_name:
                        _module_registry[meta_name] = module
                
                # Also index by import path
                _module_registry[module_name] = module
                
            except Exception as e:
                logger.debug(f"Skipping module {module_name} during registry load: {e}")
                continue
                
        _registry_loaded = True
        logger.info(f"Registry loaded with {len(_module_registry)} module mappings.")
        
    except Exception as e:
        logger.error(f"Error building module registry: {e}")


def get_module_descriptions() -> str:
    """Return a formatted string of available modules and their purposes for the LLM."""
    if not _registry_loaded:
        _load_registry()
    
    descriptions = []
    # Use a set to avoid duplicates between meta names and import paths
    processed_modules = set()
    
    for name, module in _module_registry.items():
        if module in processed_modules:
            continue
            
        meta = getattr(module, MODULE_META_ATTR, None)
        if meta:
            m_name = meta.get("name", name)
            m_desc = meta.get("description", "No description provided")
            m_cat = meta.get("category", "General")
            # Provide the internal ID (name) as the primary identifier for the LLM
            descriptions.append(f"- ID: {name} | Name: {m_name} ({m_cat}): {m_desc}")
            processed_modules.add(module)
            
    return "\n".join(sorted(descriptions))


def _verify_module(module: Any):
    """Ensure module has the required interface (run function)."""
    if not hasattr(module, "run"):
        raise AttributeError(f"Module {module.__name__} is missing mandatory 'run()' function.")


if __name__ == "__main__":
    """Display all available modules when script is run directly."""
    console.print(list_modules())
