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
    """Retrieve a module by metadata name or import path.
    
    Searches the modules directory for a module matching the given name.
    Name can be either the MODULE_META name field or the full import path.
    
    Args:
        name: Module name (from MODULE_META) or import path (e.g., "modules.web.xss").
    
    Returns:
        Loaded module object.
    
    Raises:
        ModuleNotFoundError: If module with given name is not found.
    """
    modules_path: str = str(Path.cwd() / MODULES_DIR)
    
    try:
        # Walk through modules and match by name
        for loader, module_name, is_pkg in pkgutil.walk_packages(
            [modules_path], prefix=f"{MODULES_DIR}."
        ):
            # Skip subpackages
            if is_pkg:
                continue
            
            try:
                module = importlib.import_module(module_name)
                meta: Optional[Dict[str, Any]] = getattr(
                    module, MODULE_META_ATTR, None
                )
                
                # Match by MODULE_META name or import path
                if meta and (meta.get("name") == name or module_name == name):
                    logger.info(f"Loaded module: {name} from {module_name}")
                    return module
                    
            except ImportError:
                continue
            except Exception as e:
                logger.warning(f"Error checking module {module_name}: {e}")
                continue
        
        # Module not found
        logger.error(f"Module not found: {name}")
        raise ModuleNotFoundError(f"Module '{name}' not found in DARKWIN library.")
        
    except ModuleNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving module '{name}': {e}", exc_info=True)
        raise ModuleNotFoundError(f"Failed to load module '{name}': {e}")


if __name__ == "__main__":
    """Display all available modules when script is run directly."""
    console.print(list_modules())
