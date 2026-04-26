import importlib
import pkgutil
import os
from rich.table import Table
from rich.console import Console

console = Console()

def list_modules():
    """
    Dynamically discovers and lists all modules under the 'modules' directory.
    """
    table = Table(title="DARKWIN Loaded Modules")
    table.add_column("Category", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    table.add_column("Version", style="dim")

    modules_path = os.path.join(os.getcwd(), "modules")
    
    # Grouping by category
    module_data = []

    for loader, module_name, is_pkg in pkgutil.walk_packages([modules_path], prefix="modules."):
        if is_pkg:
            continue
            
        try:
            module = importlib.import_module(module_name)
            meta = getattr(module, "MODULE_META", None)
            if meta:
                module_data.append({
                    "category": meta.get("category", "General"),
                    "name": meta.get("name", module_name),
                    "description": meta.get("description", "No description"),
                    "version": meta.get("version", "1.0.0")
                })
        except Exception:
            continue

    # Sort and add to table
    for m in sorted(module_data, key=lambda x: x['category']):
        table.add_row(m['category'], m['name'], m['description'], m['version'])

    return table

def get_module(name: str):
    """
    Retrieves a module by its metadata name or import path.
    """
    modules_path = os.path.join(os.getcwd(), "modules")
    for loader, module_name, is_pkg in pkgutil.walk_packages([modules_path], prefix="modules."):
        if is_pkg:
            continue
        try:
            module = importlib.import_module(module_name)
            meta = getattr(module, "MODULE_META", None)
            if meta and (meta.get("name") == name or module_name == name):
                return module
        except Exception:
            continue
    
    raise ModuleNotFoundError(f"Module '{name}' not found in DARKWIN library.")

if __name__ == "__main__":
    console.print(list_modules())
