# DARKWIN Module Development Guide
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

DARKWIN is built on a highly modular architecture. This guide explains how to build, test, and integrate new modules into the engine using the project's modern code conventions.

---

## Table of Contents
1. [Module Types](#module-types)
2. [Required Conventions](#required-conventions)
3. [The BaseModule Class](#the-basemodule-class)
4. [Module Metadata (MODULE_META)](#module-metadata-module_meta)
5. [Exception Handling Rules](#exception-handling-rules)
6. [Testing Your Module](#testing-your-module)
7. [Category Reference](#category-reference)

---

## Module Types

DARKWIN supports two types of modules:

### 1. Standalone Script (Simple)
Ideal for small tools or quick integrations.

```python
from typing import Dict, List, Any

MODULE_META: Dict[str, str] = {
    "name": "My Simple Module",
    "category": "Fuzzing",
    "description": "Scans for .env files",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict[str, Any]]:
    """Execute the module.

    Args:
        target: Target domain or URL.
        scan_id: Unique scan identifier.
        config: Application configuration dict.

    Returns:
        List of finding dictionaries.
    """
    return []
```

### 2. BaseModule Child (Recommended)
Preferred for complex modules that require persistence, logging, and verification.

```python
from core.base_module import BaseModule

class MyAdvancedModule(BaseModule):
    async def run(self, config: dict) -> None:
        self.log(f"Starting scan on {self.target}")
        self.add_finding(
            vuln_type="Sensitive File",
            severity="Medium",
            endpoint=f"{self.target}/.env",
            description="Found an exposed .env file."
        )
```

---

## Required Conventions

All modules **MUST** follow these conventions (review will reject violations):

### Exception Handling
- **NEVER** use bare `except:` or `except Exception:`.
- Use specific types: `httpx.RequestError`, `OSError`, `ValueError`, `FileNotFoundError`, `subprocess.CalledProcessError`, etc.

### File Operations
- Use `pathlib.Path` exclusively — no `os.path.*`.
- Use `Path.read_text()`, `Path.write_bytes()`, `Path.unlink(missing_ok=True)`.

### HTTP Requests
- Use `httpx` (not `requests`).
- Always specify timeouts: `httpx.get(url, timeout=30)`.
- Catch `httpx.RequestError` and `httpx.HTTPStatusError`.

### Subprocess Calls
- Always specify `check=True` or `check=False` on `subprocess.run()`.
- Catch `subprocess.CalledProcessError` and `FileNotFoundError`.

### Docstrings
- PEP 257 style with `Args:`, `Returns:`, `Raises:` sections.

---

## The BaseModule Class (`core/base_module.py`)

Inheriting from `BaseModule` gives you several built-in advantages:
- **`self.logger`**: Pre-configured logger with `scan_id` context.
- **`self.add_finding()`**: Automatically records the finding to the database and triggers verification.
- **`self.target` & `self.scan_id`**: Automatically handled in `__init__`.

---

## Module Metadata (`MODULE_META`)

Every module **MUST** define a `MODULE_META` dictionary at the top of the file:

| Field | Description |
|-------|-------------|
| `name` | Human-readable name of the module |
| `category` | One of the pre-defined categories (see below) |
| `description` | Brief explanation of what the module does |
| `version` | Version string (e.g., "1.2.0") |
| `author` | (Optional) Your name or handle |

---

## Exception Handling Rules

### DO
```python
# GOOD: Specific exception types
try:
    r = httpx.get(url, timeout=30)
    r.raise_for_status()
except httpx.RequestError as e:
    logger.error(f"HTTP request failed: {e}")
except httpx.HTTPStatusError as e:
    logger.error(f"HTTP {e.response.status_code}: {e}")
```

### DON'T
```python
# BAD: Bare except hides bugs
try:
    r = httpx.get(url, timeout=30)
except:
    pass

# BAD: Too broad
try:
    r = httpx.get(url, timeout=30)
except Exception as e:
    logger.error(f"Failed: {e}")
```

---

## Testing Your Module

Test your module in isolation:

```python
import asyncio
from modules.my_module import run

async def test() -> None:
    config = {"timeout": 30}
    results = await run("example.com", "test_scan_id", config)
    print(results)

asyncio.run(test())
```

Also verify compilation:
```bash
python -m py_compile modules/my_module.py
```

---

## Category Reference

Use these exact strings in your `MODULE_META`:
- `Reconnaissance`
- `Attack Surface`
- `Web Scanning`
- `Vulnerability Engine`
- `Fuzzing`
- `Network`
- `Exploit Engine`
- `AI Security`

---

<div align="center">
<b>Extend the Intelligence of DARKWIN</b><br/>
(C) 2026 ARYAN AHIRWAR (VIPHACKER.100)
</div>
