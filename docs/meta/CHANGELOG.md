# DARKWIN-NGASR Changelog
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

---

### [2.0.3] - 2026-06-20
**Codebase Modernization — Zero Bare Exceptions, pathlib, httpx**

This release systematically upgrades all 142 Python source files to modern Python security and style best practices:

- **Exception Handling Overhaul**: Replaced every bare `except:` and `except Exception:` with specific exception types (`httpx.RequestError`, `subprocess.CalledProcessError`, `json.JSONDecodeError`, `OSError`, `shodan.APIError`, `redis.RedisError`, `dns.exception.DNSException`, etc.) across all modules, integrations, AI agents, tests, and core files.
- **pathlib Migration**: All `os.path.join()`, `os.path.exists()`, `os.remove()`, `os.path.abspath()` calls replaced with `pathlib.Path` equivalents (`/`, `.exists()`, `.unlink(missing_ok=True)`, `.resolve()`).
- **httpx Adoption**: All remaining `import requests` usages migrated to `httpx` with proper timeout and error handling.
- **subprocess Hardening**: Every `subprocess.run()` call explicitly specifies `check=True` or `check=False` for deterministic failure behavior.
- **PEP 257 Docstrings**: Module-level, function-level, and class-level docstrings with `Args:`, `Returns:`, `Raises:` sections across every file.
- **Context Manager Correctness**: Fixed all remaining standalone `open()` calls (not inside `with`) to use proper context managers.
- **File encoding**: `encoding="utf-8"` on all file writes; `missing_ok=True` on all `Path.unlink()` calls.
- **Compilation & Test Verification**: All 142 project `.py` files pass `python -m py_compile`; all 11 pytest tests pass.

Files upgraded by category:
- **Core**: `darkwin.py`, `database.py`, `logging_system.py`, `pipeline_engine.py`, `command_router.py`, `scheduler.py`, `module_loader.py`, `agent_loop.py`, `socketio_handler.py`, `config_manager.py`, `setup_wizard.py`, `interactive_shell.py`, `migrations/init_db.py`, `compliance/scope_enforcer.py`, `compliance/privacy_scrubber.py`, `compliance/data_retention_manager.py`, `doctor.py` + all modules under `ai/`, `ai_security/`, `attack_surface/`, `exploit_engine/`, `fuzzing/`, `network/`, `post_exploitation/`, `reconnaissance/`, `reporting/`, `web_scanning/`
- **Integrations**: `shodan_api.py`, `virustotal_api.py`, `github_api.py`, `censys_api.py`, `api_utils.py`, `docx_generator.py`, `notifications/discord/`, `notifications/slack/`, `shodan/shodan_integration.py`, `censys/censys_integration.py`
- **Dashboard Backend**: `app.py`, `api_v1.py`, `auth_manager.py`, `findings.py`, `scans.py`, `socket_manager.py`
- **Tests**: `test_robustness.py`, `test_core.py`, `test_db.py`, `test_scanners.py`, `conftest.py`
- **Automation**: `ci_cd_integration.py`, `auto_bug_hunter/hunter.py`
- **Bugfix**: Fixed pre-existing `NameError: name 'Dict' is not defined` in `modules/web_scanning/crawler_engine/crawler.py:15`

### [2.0.2] - 2026-05-10
**Interactivity & Resilience Overhaul**
- **Dashboard Interactivity**:
    - Resolved **CORS Policy Blocks** by explicitly configuring permissive cross-origin headers in the Flask backend.
    - Improved **Report Generation Feedback** in the UI with loading states, error handling, and direct browser-based download links.
- **Windows Runtime Hardening**:
    - Fixed terminal-wide 'charmap' encoding crashes by enforcing UTF-8 rendering in the Rich console.
    - Implemented **Encoding Fallback** for report synthesis.
- **AI Backend Resilience**:
    - Hardened the `AIAgentManager` against **WinError 10061 (Connection Refused)**.
- **Data Persistence**:
    - Improved **Vulnerability Finding Capture** with defensive type checking.

### [2.0.1] - 2026-05-10
**Zenith Stabilization & Reporting Overhaul**
- Fixed `darkwin fuzz`, `darkwin watch` import paths.
- Implemented `darkwin reports` command.
- Fixed sync-async mismatch in `test_scanners.py`.
- Cross-platform permission detection in `logging_system.py`.
- Fixed `UnicodeEncodeError` during AI report generation on Windows.
- "No-Persistence Mode" fallback detection.

### [2.0.0] - 2026-05-10
**Apex — Stability & Architecture Hardening**
- Module Registry Cache for 10x faster tool discovery.
- Phase-based Pipeline sequencing.
- Timezone-aware UTC datetime operations.
- Comprehensive pytest suite.

### [1.2.0] - 2026-05-10
**Bug Bounty One-Liner Integration & Performance Suite**
- Upgraded LFI, Open Redirect, XSS, SQLi scanners.
- New modules: CORS, SSRF, Subdomain Takeover, Secret Finder, Prototype Pollution, CVE Scanner.
- `core/one_liner_adapter.py` for safe shell pipeline execution.

### [1.0.7] - 2026-05-09
**Self-Healing Database & Robust Fallback**
- Lazy Database Initialization with PostgreSQL-to-SQLite fallback.
- Automated table creation for fallback databases.

### [1.0.6] - 2026-05-09
**Target Scope & History Management**
- `darkwin targets`, `darkwin history` commands.

### [1.0.4] - 2026-05-02
**Package Structure Restoration**
- Created missing `__init__.py` files across all packages.

### [1.0.3] - 2026-05-02
**Vulnerability Template Synchronizer & API Monitoring**
- `darkwin update-templates`, enhanced `/health` endpoint.

### [1.0.2] - 2026-05-02
**Core Testing & CI Linting**
- `core/tests/test_core.py`, flake8 linting in CI.

### [1.0.1] - 2026-05-02
**Documentation & Update Command**
- `darkwin update` command, README overhaul.

### [1.0.0] - 2026-05-02
**Zenith Phase — Full Release**
- Agentic Reasoning Loop, TUI, Shell, Ghost Mode, Mesh, Proxy Pool, Vuln Verifier, Notifications, Cache, Reporting, 3D Map, CI/CD.

### [0.9.0] - 2026-04-26
**Initial Release**
- Core Engine, 117+ modules, Celery/Redis, Dashboard, OpenAI integration.

---

(C) 2026 ARYAN AHIRWAR (VIPHACKER.100)
