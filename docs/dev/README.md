# DARKWIN-NGASR Developer Guide
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

This guide is intended for developers who wish to understand the inner workings of DARKWIN-NGASR, contribute to the core engine, or build complex integrations.

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Codebase Conventions](#codebase-conventions)
3. [Core Components Deep Dive](#core-components-deep-dive)
4. [The Pipeline Engine](#the-pipeline-engine)
5. [Agentic Reasoning Loop](#agentic-reasoning-loop)
6. [Database Schema & Models](#database-schema--models)
7. [Distributed Mesh Mechanics](#distributed-mesh-mechanics)
8. [Stealth & Evasion Engineering](#stealth--evasion-engineering)
9. [Testing & QA](#testing--qa)

---

## System Architecture

DARKWIN follows a **Modular Monolith** architecture with distributed worker capabilities.

- **Frontend**: Next.js 16 (Dashboard)
- **Backend API**: Flask (Socket.io for real-time logs)
- **Core Engine**: Python 3.11+ (Asyncio-driven)
- **Data Layer**: PostgreSQL (Scan data) + Redis (Task queue & Mesh registry)

---

## Codebase Conventions

All code in this project follows these strict conventions:

### Exception Handling
- **NEVER** use bare `except:` or `except Exception:`.
- Always catch specific types: `httpx.RequestError`, `OSError`, `ValueError`, `json.JSONDecodeError`, `subprocess.CalledProcessError`, etc.
- Multiple `except` clauses for different error types are encouraged.

### File Operations
- Use `pathlib.Path` exclusively — no `os.path.*`.
- Always use context managers (`with` statements) for file I/O.
- Specify `encoding="utf-8"` on text file operations.
- Use `.unlink(missing_ok=True)` instead of `os.remove()`.

### HTTP Client
- Use `httpx` (not `requests`).
- Always specify timeouts.
- Handle `httpx.RequestError` and `httpx.HTTPStatusError`.

### Subprocess
- Always specify `check=True` or `check=False` explicitly.
- Catch `subprocess.CalledProcessError`, `subprocess.TimeoutExpired`, `FileNotFoundError`.

### Docstrings
- PEP 257 style with `Args:`, `Returns:`, `Raises:` sections on all public APIs.

---

## Core Components Deep Dive

### 1. `core/darkwin.py` (The Entry Point)
The main CLI entry point using `click`. It routes commands to the `command_router.py`.

### 2. `core/command_router.py` (The Brain)
Handles all CLI command logic, argument parsing, and UI output formatting using `rich`.

### 3. `core/module_loader.py` (Dynamic Loading)
Recursively scans the `modules/` directory for any `.py` files containing `MODULE_META` and a `run()` function. It supports hot-loading and categorization via a registry cache.

### 4. `core/database.py` & `core/models.py` (Persistence)
SQLAlchemy-based ORM. Supports PostgreSQL for production and SQLite as a zero-persistence fallback with lazy initialization.

---

## The Pipeline Engine (`core/pipeline_engine.py`)

Pipelines are sequences of `PipelineStep` objects.
- **Phased Execution**: Steps can be assigned to phases (e.g., Phase 1: Recon, Phase 2: Scanning).
- **Context Sharing**: Data discovered in early steps is passed to subsequent steps.
- **Error Handling**: Graceful degradation with specific exception types for step failures.

```python
from core.pipeline_engine import Pipeline, PipelineStep

pipeline = Pipeline("MyCustomPipeline", [
    PipelineStep(name="Step 1", module_fn=my_module, args=[target, scan_id], phase=1),
])
pipeline.run(target, scan_id)
```

---

## Agentic Reasoning Loop (`core/agent_loop.py`)

The Agentic Loop mimics a human security researcher.
1. **Observation**: Extracts context from the database (discovered ports, techs).
2. **Analysis**: Sends context to the LLM with a prompt describing available modules.
3. **Decision**: AI returns a JSON plan (which module to run next and why).
4. **Action**: The engine executes the recommended module and updates the reasoning history.

---

## Database Schema & Models

- **Target**: Represents a domain/IP in scope.
- **Scan**: A specific execution session.
- **Finding**: A verified vulnerability or interesting observation.
- **Screenshot**: Path to visual evidence.
- **MeshNode**: Registry for distributed workers.

---

## Distributed Mesh Mechanics

DARKWIN uses Redis as a central heartbeat and task queue system.
- **Registry**: Nodes register themselves in a Redis hash with system stats.
- **Orchestration**: Tasks are pushed to Redis, and workers pull them based on their capabilities.
- **Global Rate Limiting**: `rate_limiter.py` ensures total request volume across all nodes does not exceed threshold.

---

## Stealth & Evasion Engineering (`core/stealth.py`)

- **Fingerprint Randomization**: Uses `curl-cffi` to mimic different browser TLS fingerprints.
- **User-Agent Churn**: Rotates through thousands of real-world UA strings.
- **Adaptive Jitter**: Calculates delays based on Gaussian distribution.
- **WAF Detection**: Automatically detects blocking and triggers proxy rotation.

---

## Testing & QA

- **Unit Tests**: Located in `tests/`. Run via `pytest`.
- **System Diagnostics**: `core/doctor.py` acts as integration test for environment.
- **Compilation Check**: `python -m py_compile` on all files before committing.

```bash
# Run all tests
pytest tests/ -v

# Verify compilation
python -m py_compile <file>.py
```

---

<div align="center">
<b>DARKWIN-NGASR Developer Resources</b><br/>
(C) 2026 ARYAN AHIRWAR (VIPHACKER.100)
</div>
