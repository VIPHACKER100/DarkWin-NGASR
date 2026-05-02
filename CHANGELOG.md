# DARKWIN-NGASR Changelog
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

---

### [1.0.5] - 2026-05-02
**Bug Fixes & Environment Stability**
- Fixed `IndentationError` and `SyntaxWarning` in the `about` command ASCII logo.
- Replaced `--user` pip installs with a proper `.venv` virtual environment in `setup.sh` to permanently resolve `typing_extensions` shadowing on Python 3.13.
- Improved `doctor --fix` to guide users to activate `.venv` instead of silently failing.
- Dynamically add project root to `sys.path` in `core/darkwin.py` to fix `ModuleNotFoundError`.

### [1.0.4] - 2026-05-02
**Package Structure Restoration**
- Created missing `__init__.py` files across all packages (`core`, `modules`, `pipelines`, `ai`, `automation`, `integrations`, `dashboards`).
- Fixed `darkwin` CLI entry point resolving the wrong module path.

### [1.0.3] - 2026-05-02
**Vulnerability Template Synchronizer & API Monitoring**
- Added `darkwin update-templates` to sync latest Nuclei templates automatically.
- Enhanced `/health` endpoint with real Database and Redis connectivity checks.

### [1.0.2] - 2026-05-02
**Core Testing & CI Linting**
- Added `core/tests/test_core.py` with unit tests for CacheManager, GhostMode, and VulnVerifier.
- Integrated `flake8` linting into GitHub Actions CI pipeline.
- Added `darkwin test` CLI command to run the test suite on-demand.

### [1.0.1] - 2026-05-02
**Documentation & Update Command**
- Added `darkwin update` command to pull latest changes and re-run setup.
- Overhauled `README.md` with full Zenith feature set and CLI reference table.
- Updated `AGENTS.md` with the Sentinel agent documentation.

### [1.0.0] - 2026-05-02
**Zenith Phase — Full Release**
- Autonomous Agentic Reasoning Loop (`core/agent_loop.py`) with LLM-driven tactical planning.
- Real-time Terminal UI (`core/tui_engine.py`) using Rich Live for scan telemetry.
- Interactive REPL Shell (`core/interactive_shell.py`) with tab-completion via `prompt-toolkit`.
- Ghost Mode stealth engine (`core/stealth.py`) with randomized TLS/UA fingerprints and jitter.
- Distributed Mesh node registry (`core/mesh_manager.py`) via Redis.
- Proxy Rotation pool (`core/proxy_manager.py`) for WAF/IP-ban bypass.
- Vulnerability Verification Engine (`core/vuln_verifier.py`) for false-positive elimination.
- Multi-channel Notification Manager (`core/notification_manager.py`) — Discord & Slack.
- Redis-backed Cache Manager (`core/cache_manager.py`) for scan performance.
- PDF/HTML/Markdown AI Report generation (`core/reporting_engine.py`) with `fpdf2`.
- 3D Neural Attack Surface Map (`AttackSurfaceGraph.tsx`) using Three.js & ForceGraph.
- Real-time Socket.io log streaming from scan engine to Next.js dashboard.
- GitHub Actions CI/CD pipeline with linting and Docker build validation.
- Full Docker Compose orchestration for API, Worker, and Dashboard services.
- `darkwin about`, `darkwin shell`, `darkwin mesh`, `darkwin proxy`, `darkwin report` commands.

### [0.9.0] - 2026-04-26
**Initial Release**
- Core Engine with Pydantic configuration and Rich logging.
- Distributed task execution via Celery and Redis.
- Over 117 modules across 18 scan phases.
- Real-time Dashboard with Flask/SocketIO backend.
- AI-backed vulnerability analysis and reasoning via OpenAI.

---
© 2026 ARYAN AHIRWAR (VIPHACKER.100)
