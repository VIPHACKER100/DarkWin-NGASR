# DARKWIN Module Development Guide
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

DARKWIN is built on a modular architecture. Each module must follow a strict interface to be correctly loaded by the engine.

### Module Structure
DARKWIN supports both synchronous and asynchronous modules. As of v2.0.1, **asynchronous** modules are preferred for better performance.

#### Async Module (Preferred)
```python
MODULE_META = {
    "name": "Async Module",
    "category": "Category",
    "description": "Async example",
    "version": "1.0.0"
}

async def run(target: str, scan_id: str, config: dict):
    # Async logic goes here
    # findings = await some_async_task()
    return []
```

#### Legacy Sync Module
```python
def run(target: str, scan_id: str, config: dict):
    # Sync logic goes here
    return []
```

### Categories
- Reconnaissance
- Attack Surface
- Web Scanning
- Vulnerability Engine
- Fuzzing
- Network
- Exploit Engine
- Post-Exploitation
- AI Security
- Reporting

---
© 2026 ARYAN AHIRWAR (VIPHACKER.100)
