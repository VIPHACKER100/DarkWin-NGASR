# DARKWIN-NGASR Changelog
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

---

### [2.0.1] - 2026-05-10
**Zenith Stabilization & Reporting Overhaul**
- **AI Intelligence**:
    - Implemented **Dynamic Module Registry Injection** to eliminate AI hallucinations and ensure 100% valid task planning.
    - Optimized reasoning prompts for **NVIDIA NIM (Gemma-3)** security models.
- **Reporting & Documentation**:
    - Added **DOCX Report Generation** support for professional Microsoft Word security assessments.
    - Updated **Memory Map** and **Roadmap** to reflect full 150-step completion (Version 2.0.0).
- **Environment Resilience**:
    - Added self-healing **sys.path resolution** in `doctor.py` to allow direct execution in various CI/CD environments.
    - Implemented **Silence Warnings** logic in the logger to suppress repeating permission-denied noise.
    - Updated documentation for `_sqlite3` missing module errors on Kali Linux.

### [2.0.0] - 2026-05-10
**Apex — Stability & Architecture Hardening**
- **Architecture Hardening**:
    - Implemented **Module Registry Cache** in `core/module_loader.py` for 10x faster tool discovery.
    - Upgraded **Pipeline Engine** with strict phase-based sequencing (Recon → Intel → Vuln).
    - Unified versioning and authorship metadata via `core/__version__.py`.
    - Migrated all datetime operations to **Timezone-Aware UTC** for reliable distributed logging.
- **Operational Reliability**:
    - Hardened **Database Session Management** to prevent leaks during long-running hunts.
    - Improved **Self-Healing Fallbacks** for Cache and Database services.
    - Added comprehensive **Pytest Suite** covering config, caching, and verifier logic.
- **Feature Completion**:
    - Implemented full logic for `fuzz`, `exploit`, `cloud`, `dashboard`, and `mesh` CLI commands.
    - Integrated **Celery Beat** for robust periodic task and scan scheduling.
    - Expanded **VulnVerifier** with LFI, SSRF, and Redirect checks + AI-assisted triage.
    - Migrated to **Environment-Variable (.env)** secrets management for production security.
- **Reporting & UI**:
    - Upgraded **PDF Reporting** with full Unicode support and AI-synthesized executive summaries.
    - Stabilized **3D Neural Attack Surface** graph synchronization with real-time findings.

### [1.2.0] - 2026-05-10
**Bug Bounty One-Liner Integration & Performance Suite**
- **Enhanced Vulnerability Engines**:
    - Upgraded **LFI Scanner** with passive discovery and Base64 traversal support.
    - Upgraded **Open Redirect Scanner** with CRLF and protocol-relative bypasses.
    - Upgraded **XSS Scanner** with `dalfox` NDJSON support and evasion flags.
    - Upgraded **SQLi & NoSQL Scanners** to full asynchronous execution with aggressive bug bounty flags.
- **New Detection Modules**:
    - **CORS Misconfiguration Scanner**: Detects Origin reflection and insecure credential policies.
    - **Subdomain Takeover Scanner**: Signature-based detection for 10+ services + Nuclei integration.
    - **SSRF Scanner**: Specialized testing for cloud metadata and internal endpoint leakage.
    - **Secret & API Key Finder**: High-fidelity regex scanning for leaked AWS, GitHub, and Slack tokens.
    - **Prototype Pollution**: Added detection for client-side prototype pollution vulnerabilities.
    - **High-Impact CVE Scanner**: Consolidated checks for F5, Cisco, vBulletin, and Microweber.
- **Core Improvements**:
    - Integrated `core/one_liner_adapter.py` for safe shell pipeline execution.
    - Upgraded `Pipeline` engine to natively support `asyncio` modules.
    - Updated `js_analyzer` regex for broader endpoint and secret discovery.
    - Standardized `MODULE_META` across all modules for better discovery.

### [1.0.7] - 2026-05-09
**Self-Healing Database & Robust Fallback**
- Implemented **Lazy Database Initialization** in `core/database.py` to prevent CLI crashes when DB is unreachable.
- Implemented `create_robust_engine` with automatic PostgreSQL-to-SQLite fallback.
- Added specific diagnostic logging for "Password Authentication Failed" and "Database Does Not Exist" errors.
- Improved error handling for environments missing the `_sqlite3` module (e.g., incomplete Python builds on Kali).
- Aligned default `config.yaml` with `docker-compose.yml` credentials (`darkwin_pass`).
- Added automated table creation during engine initialization for fallback databases.
- Updated `TROUBLESHOOTING.md` with comprehensive database recovery steps.

### [1.0.6] - 2026-05-09
**Target Scope & History Management**
- Implemented `darkwin targets` command for managing multi-target scope.
- Implemented `darkwin history` command to view past scan results and status.
- Added `darkwin update` improvements for better git pull handling.

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
