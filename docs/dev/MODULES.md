# 🛠️ DARKWIN Module Development Guide
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

DARKWIN is built on a highly modular architecture. This guide explains how to build, test, and integrate new modules into the engine.

---

## 📑 Table of Contents
1. [Module Types](#-module-types)
2. [The BaseModule Class](#-the-basemodule-class)
3. [Module Metadata (MODULE_META)](#-module-metadata-module_meta)
4. [Recording Findings](#-recording-findings)
5. [Automated Verification](#-automated-verification)
6. [Testing Your Module](#-testing-your-module)
7. [Category Reference](#-category-reference)

---

## 🔌 Module Types

DARKWIN supports two types of modules:

### 1. Standalone Script (Simple)
Ideal for small tools or quick integrations.
```python
MODULE_META = {
    "name": "My Simple Module",
    "category": "Fuzzing",
    "description": "Scans for .env files",
    "version": "1.0.0"
}

async def run(target: str, scan_id: str, config: dict):
    # Logic here
    return [] # Return findings as a list of dicts
```

### 2. BaseModule Child (Recommended)
Preferred for complex modules that require persistence, logging, and automated verification.
```python
from core.base_module import BaseModule

class MyAdvancedModule(BaseModule):
    async def run(self, config: dict):
        self.log(f"Starting scan on {self.target}")
        # ... logic ...
        self.add_finding(
            vuln_type="Sensitive File",
            severity="Medium",
            endpoint=f"{self.target}/.env",
            description="Found a exposed .env file."
        )
```

---

## 🏗️ The BaseModule Class (`core/base_module.py`)

Inheriting from `BaseModule` gives you several built-in advantages:
- **`self.logger`**: Pre-configured logger with `scan_id` context.
- **`self.add_finding()`**: Automatically records the finding to the database and triggers verification.
- **`self.target` & `self.scan_id`**: Automatically handled in `__init__`.

---

## 📝 Module Metadata (`MODULE_META`)

Every module **MUST** define a `MODULE_META` dictionary at the top of the file:

| Field | Description |
|---|---|
| `name` | Human-readable name of the module |
| `category` | One of the pre-defined categories (see below) |
| `description` | Brief explanation of what the module does |
| `version` | Version string (e.g., "1.2.0") |
| `author` | (Optional) Your name or handle |

---

## 💎 Recording Findings

Use `self.add_finding()` to record vulnerabilities. This method takes the following arguments:
- `vuln_type`: Name of the vulnerability (e.g., "XSS", "SQL Injection").
- `severity`: "Critical", "High", "Medium", "Low", or "Info".
- `endpoint`: The specific URL or asset where the finding was discovered.
- `description`: A detailed explanation for the report.
- `payload`: (Optional) The specific payload used to trigger the vulnerability.

---

## ✅ Automated Verification

When you record a finding via `BaseModule.add_finding()`, DARKWIN automatically:
1. **Queues a verification task** in the background.
2. **Executes `core/vuln_verifier.py`** to confirm exploitability.
3. **Updates the `verified` status** in the database.
4. **Sends a notification** to Discord/Slack if the finding is High or Critical and verified.

---

## 🧪 Testing Your Module

You can test your module in isolation using the `darkwin test` command or by creating a standalone test script.

**Isolated Execution Script:**
```python
import asyncio
from modules.my_module import run

async def test():
    config = {"timeout": 30}
    results = await run("example.com", "test_scan_id", config)
    print(results)

asyncio.run(test())
```

---

## 📚 Category Reference

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
© 2026 ARYAN AHIRWAR (VIPHACKER.100)
</div>
