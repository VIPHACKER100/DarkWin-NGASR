# 🏗️ DARKWIN-NGASR Developer Guide
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

This guide is intended for developers who wish to understand the inner workings of DARKWIN-NGASR, contribute to the core engine, or build complex integrations.

---

## 📑 Table of Contents
1. [System Architecture](#-system-architecture)
2. [Core Components Deep Dive](#-core-components-deep-dive)
3. [The Pipeline Engine](#-the-pipeline-engine)
4. [Agentic Reasoning Loop](#-agentic-reasoning-loop)
5. [Database Schema & Models](#-database-schema--models)
6. [Distributed Mesh Mechanics](#-distributed-mesh-mechanics)
7. [Stealth & Evasion Engineering](#-stealth--evasion-engineering)
8. [Testing & QA](#-testing--qa)

---

## 🏗️ System Architecture

DARKWIN follows a **Modular Monolith** architecture with distributed worker capabilities.

- **Frontend**: Next.js 16 (Dashboard)
- **Backend API**: Flask (Socket.io for real-time logs)
- **Core Engine**: Python 3.11+ (Asyncio-driven)
- **Data Layer**: PostgreSQL (Scan data) + Redis (Task queue & Mesh registry)

---

## 🧠 Core Components Deep Dive

### 1. `core/darkwin.py` (The Entry Point)
The main CLI entry point using `click`. It routes commands to the `command_router.py`.

### 2. `core/command_router.py` (The Brain)
Handles all CLI command logic, argument parsing, and UI output formatting using `rich`.

### 3. `core/module_loader.py` (Dynamic Loading)
Recursively scans the `modules/` directory for any `.py` files containing `MODULE_META` and a `run()` function. It supports hot-loading and categorization.

### 4. `core/database.py` & `core/models.py` (Persistence)
SQLAlchemy-based ORM. Supports PostgreSQL for production and SQLite as a zero-persistence fallback.

---

## 🚀 The Pipeline Engine (`core/pipeline_engine.py`)

Pipelines are sequences of `PipelineStep` objects.
- **Phased Execution**: Steps can be assigned to phases (e.g., Phase 1: Recon, Phase 2: Scanning).
- **Context Sharing**: Data discovered in early steps (e.g., subdomains) is passed to subsequent steps.
- **Error Handling**: Graceful degradation if a single module fails.

```python
from core.pipeline_engine import Pipeline, PipelineStep

pipeline = Pipeline("MyCustomPipeline", [
    PipelineStep(name="Step 1", module_fn=my_module, args=[target, scan_id], phase=1),
    # ...
])
pipeline.run(target, scan_id)
```

---

## 🤖 Agentic Reasoning Loop (`core/agent_loop.py`)

The Agentic Loop mimics a human security researcher.
1. **Observation**: Extracts context from the database (discovered ports, techs).
2. **Analysis**: Sends context to the LLM (OpenAI/NIM) with a prompt describing available modules.
3. **Decision**: AI returns a JSON plan (which module to run next and why).
4. **Action**: The engine executes the recommended module and updates the "Reasoning History".

### AI Backends
The loop uses `ai/multi_step_reasoning.py` to abstract different AI providers.

---

## 📦 Database Schema & Models

- **Target**: Represents a domain/IP in scope.
- **Scan**: A specific execution session.
- **Finding**: A verified vulnerability or interesting observation.
- **Screenshot**: Path to visual evidence.
- **MeshNode**: Registry for distributed workers.

---

## 🌐 Distributed Mesh Mechanics

DARKWIN uses Redis as a central "Heartbeat" and "Task Queue" system.
- **Registry**: Nodes register themselves in a Redis hash with system stats.
- **Orchestration**: Tasks are pushed to Redis, and workers pull them based on their capabilities.
- **Global Rate Limiting**: `rate_limiter.py` ensures that the total request volume across all nodes does not exceed the target's threshold.

---

> **Related in-depth guides:**
> - [Pipeline Architecture](PIPELINES.md) — Pipeline engine, phases, context sharing, custom pipelines
> - [AI Agent System](AI_AGENTS.md) — Agentic loop, reasoning backends, prompt engineering, tuning
> - [Integration Development](INTEGRATIONS.md) — Adding Shodan/Censys/VT and custom integrations
> - [Testing Guide](TESTING.md) — Test suite structure, writing tests, mocking, CI

## 👻 Stealth & Evasion Engineering (`core/stealth.py`)

The stealth engine is designed to defeat modern WAFs and IDSs.
- **Fingerprint Randomization**: Uses `curl-cffi` to mimic different browser TLS fingerprints (Chrome, Firefox, Safari).
- **User-Agent Churn**: Rotates through thousands of real-world UA strings.
- **Adaptive Jitter**: Calculates delays between requests based on a Gaussian distribution to simulate human behavior.
- **WAF Detection**: Automatically detects if a node is being blocked and triggers proxy rotation.

---

## 🧪 Testing & QA

- **Unit Tests**: Located in `tests/`. Run via `pytest`.
- **System Diagnostics**: `core/doctor.py` acts as an integration test for the environment.
- **Mocking**: Use `conftest.py` for mocking API responses (OpenAI, Shodan).

```bash
# Run all tests
pytest tests/

# Run specific component test
pytest tests/test_stealth.py
```

---
<div align="center">
<b>DARKWIN-NGASR Developer Resources</b><br/>
© 2026 ARYAN AHIRWAR (VIPHACKER.100)
</div>
