import importlib
import os
import pkgutil
from typing import Dict, List, Any
from rich.table import Table
from rich.console import Console

class ModuleLoader:
    def __init__(self, modules_path: str = "modules"):
        self.modules_path = modules_path
        self.loaded_modules: Dict[str, Any] = {}

    def discover_modules(self):
        """Dynamically discover and import all modules under the modules/ directory."""
        self.loaded_modules = {}
        # Iterate through all packages in the modules directory
        for loader, module_name, is_pkg in pkgutil.walk_packages([self.modules_path], prefix="modules."):
            if not is_pkg:
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, "MODULE_META"):
                        # Use the module's simple name (last part) as the key
                        short_name = module_name.split(".")[-1]
                        self.loaded_modules[short_name] = module
                except Exception as e:
                    # Logging would be good here, but keeping it simple for now
                    pass

    def list_modules(self) -> Table:
        """Returns a formatted rich Table of all loaded modules."""
        table = Table(title="DARKWIN Modules", show_header=True, header_style="bold magenta")
        table.add_column("Category", style="dim")
        table.add_column("Name", style="bold cyan")
        table.add_column("Version", justify="right")
        table.add_column("Description")

        # Group by category from MODULE_META
        sorted_modules = sorted(self.loaded_modules.values(), key=lambda m: (m.MODULE_META.get("category", "unknown"), m.MODULE_META.get("name", "")))
        
        for module in sorted_modules:
            meta = module.MODULE_META
            table.add_row(
                meta.get("category", "N/A"),
                meta.get("name", "N/A"),
                meta.get("version", "N/A"),
                meta.get("description", "No description available")
            )
        
        return table

    def get_module(self, name: str) -> Any:
        """Returns the module object by name."""
        if not self.loaded_modules:
            self.discover_modules()
        
        if name in self.loaded_modules:
            return self.loaded_modules[name]
        raise ModuleNotFoundError(f"Module '{name}' not found.")

def list_all_modules():
    loader = ModuleLoader()
    loader.discover_modules()
    console = Console()
    console.print(loader.list_modules())
