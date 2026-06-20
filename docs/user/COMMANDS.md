# 🚀 DARKWIN-NGASR Master Command Reference
## Developed by ARYAN AHIRWAR (VIPHACKER.100)

This document provides a comprehensive reference for all commands available in the DARKWIN-NGASR CLI, including advanced flags and power-user workflows.

---

## 🧠 Core Intelligence & Scanning

### `darkwin hunt`
Starts the fully autonomous agentic research loop.
```bash
# Standard autonomous hunt
darkwin hunt example.com

# Advanced: Increase reasoning depth (default 5, max 50)
darkwin hunt example.com --max-steps 15

# Advanced: Enforce a strict scope policy
darkwin hunt example.com --scope-file policies/bugbounty.json
```

### `darkwin recon`
Runs the reconnaissance-only pipeline (Passive + Active Discovery).
```bash
darkwin recon example.com
```

### `darkwin scan`
Runs the standard vulnerability assessment pipeline.
```bash
darkwin scan example.com
```

### `darkwin fuzz`
Triggers specialized fuzzing modules (Directories, Parameters, API endpoints).
```bash
darkwin fuzz example.com
```

### `darkwin cloud`
Audits cloud-specific infrastructure (S3 Buckets, Azure Blobs, GCP Storage).
```bash
darkwin cloud example.com
```

### `darkwin watch`
Initiates continuous monitoring for a target.
```bash
darkwin watch example.com
```

### `darkwin exploit`
Searches for potential exploit suggestions matching the target's stack.
```bash
darkwin exploit example.com
```

---

## 🎯 Asset & Knowledge Management

### `darkwin targets`
Manages the global target scope database.
```bash
# List all targets in scope
darkwin targets

# Add a new target
darkwin targets --add alpha.com

# Remove a target
darkwin targets --remove beta.com
```

### `darkwin wordlists`
Manages local reconnaissance and fuzzing wordlists.
```bash
# List local wordlist inventory
darkwin wordlists

# Download industry-standard wordlists (Seclists, etc.)
darkwin wordlists --download
```

### `darkwin payloads`
Browse and manage the exploit payload repository.
```bash
# View all payload categories
darkwin payloads

# Filter by type (xss, sqli, rce, lfi, etc.)
darkwin payloads --type xss
```

---

## 📊 Data & Evidence

### `darkwin history`
Audits past scan performance and results.
```bash
# View last 20 scans
darkwin history

# View last 100 scans
darkwin history --limit 100
```

### `darkwin screenshots`
Manages captured visual evidence from scans.
```bash
# List all captured screenshots
darkwin screenshots

# Filter screenshots for a specific scan
darkwin screenshots --scan-id <id>

# Instantly open the most recent screenshot
darkwin screenshots --open
```

### `darkwin logs`
Deep auditing of system and scan logs.
```bash
# View last 20 lines
darkwin logs --tail 20

# Search logs for a specific keyword or finding
darkwin logs --search "Critical"

# Follow logs in real-time (Live Stream)
darkwin logs --follow
```

### `darkwin report`
Generates AI-synthesized intelligence reports.
```bash
# Generate Markdown report (Default)
darkwin report <scan_id> --format md

# Generate Professional PDF report
darkwin report <scan_id> --format pdf

# Generate Interactive HTML report
darkwin report <scan_id> --format html
```

### `darkwin reports`
Manages and views all generated reports.
```bash
# List all generated reports
darkwin reports

# Instantly open the most recently generated report
darkwin reports --open
```

### `darkwin schedule`
Manages periodic security scans and recurring tasks.
```bash
# List all active scheduled tasks
darkwin schedule --list

# Schedule a new weekly autonomous hunt
darkwin schedule --add "hunt example.com weekly"

# Remove a scheduled task by ID
darkwin schedule --remove <id>
```

---

## 🌐 Infrastructure & Connectivity

### `darkwin mesh`
Displays the status of the distributed scanning node mesh.
```bash
darkwin mesh
```

### `darkwin proxy`
Manages the proxy rotation and stealth pool.
```bash
darkwin proxy
```

### `darkwin dashboard`
Launches the web-based Next.js HUD.
```bash
darkwin dashboard
```

---

## ⚙️ Platform Maintenance & Updates

### `darkwin update`
Synchronizes the full ecosystem (Source code + Python dependencies).
```bash
darkwin update
```

### `darkwin update-templates`
Synchronizes the latest Nuclei vulnerability templates.
```bash
darkwin update-templates
```

### `darkwin clean`
Performs platform maintenance and data purging.
```bash
# Purge system logs
darkwin clean --logs

# Purge screenshots
darkwin clean --screenshots

# Purge temp/cache files
darkwin clean --temp

# Full Platform Reset (Purge ALL)
darkwin clean --all
```

### `darkwin config`
Manages platform configuration and API keys.
```bash
# View current config (Secrets auto-masked)
darkwin config --view

# Open config.yaml in default editor
darkwin config --edit
```

---

## 🛠️ Diagnostics & Setup

### `darkwin doctor`
Runs core system diagnostics and applies self-healing fixes.
```bash
# Run diagnostics only
darkwin doctor

# Run diagnostics and attempt automated fixes
darkwin doctor --fix
```

### `darkwin troubleshoot`
Launches the interactive troubleshooting wizard.
```bash
# Start wizard
darkwin troubleshoot

# Run a quick environment check
darkwin troubleshoot --check
```

### `darkwin shell`
Launches the interactive DARKWIN REPL with tab-completion.
```bash
darkwin shell
```

### `darkwin setup`
Launches the interactive first-time configuration wizard.
```bash
darkwin setup
```

### `darkwin sysinfo`
Displays detailed hardware, OS, and environment information.
```bash
darkwin sysinfo
```

### `darkwin modules`
Lists every scan module currently loaded into the engine.
```bash
darkwin modules
```

### `darkwin test`
Runs the internal core unit and integration test suite.
```bash
darkwin test
```

### `darkwin about`
Displays platform version, author, and legal information.
```bash
darkwin about
```

### `darkwin release`
Displays the current version, codename, and full changelog history.
```bash
# View current version info
darkwin release

# View full version history (Changelog)
darkwin release --changelog
```

---

## ⚡ Power-User Workflows

### 1. The "Full Stack" Security Audit
Chain multiple pipelines for a comprehensive assessment from discovery to exploitation.
```bash
# Recon -> Scan -> Report
darkwin recon example.com && darkwin scan example.com && darkwin report <scan_id>
```

### 2. High-Fidelity Autonomous Hunting
For complex targets, increase reasoning depth to allow the AI to perform deeper lateral movement.
```bash
# Deep reasoning (30 steps) with stealth proxying
darkwin hunt example.com --max-steps 30 --proxy
```

### 3. Distributed Mesh Synchronization
Update all remote nodes simultaneously and verify their health.
```bash
# Update templates on all nodes -> Update source -> Run diagnostics
darkwin update-templates && darkwin update && darkwin doctor --fix
```

---

## 🛠️ System & Development Commands

These commands are typically run via the `Makefile` or directly for platform maintenance.

### Makefile Shortcuts
| Command | Action |
| :--- | :--- |
| `make install` | Full platform installation and dependency sync |
| `make dev` | Launch the platform in developer mode |
| `make test` | Execute the full `pytest` suite |
| `make lint` | Run code quality checks (Flake8) |
| `make docker-up` | Spin up the production Docker stack (Redis/Postgres/Next.js) |
| `make docker-down` | Tear down the production Docker stack |
| `make init-db` | Manually initialize/reset the PostgreSQL/SQLite database |
| `make clean` | Deep purge of caches and build artifacts |

### Docker Orchestration
```bash
# View live logs for all containers
docker-compose logs -f

# Restart only the worker nodes
docker-compose restart worker

# Scale the scanner nodes to 5 instances
docker-compose up -d --scale worker=5
```

---

## 🌍 Environment Configuration

DARKWIN-NGASR respects several environment variables for sensitive operations:

| Variable | Description |
| :--- | :--- |
| `APP__VERSION` | Override platform version (e.g., "2.0.0") |
| `DATABASE__URL` | Connection string for PostgreSQL or SQLite |
| `REDIS__URL` | Connection string for the Mesh task queue and cache |
| `AI__OPENAI_API_KEY` | Required for autonomous AI reasoning |
| `AI__OPENAI_MODEL` | Override the default GPT model (e.g., "gpt-4o") |
| `API_KEYS__SHODAN` | Passive reconnaissance enrichment key |
| `NOTIFICATIONS__DISCORD` | Webhook URL for Discord alerts |
| `FLASK_SECRET_KEY` | Secret key for dashboard session security |

---

## 🏴‍☠️ Bug Bounty One-Liner Toolkit

DARKWIN-NGASR integrates high-performance community one-liners. While these can be run manually, they are also utilized by the internal engine.

### Cross-Site Scripting (XSS)
Fast discovery and verification using `gau` and `dalfox`.
```bash
# Extract all URLs and pipe to dalfox for headless XSS testing
gau example.com | dalfox pipe --silence --no-color
```

### Subdomain Discovery & Takeover
Recursive subdomain enumeration with automated takeover verification.
```bash
# Find subdomains and check for takeovers via Nuclei
subfinder -d example.com -silent | nuclei -t takeover/ -silent
```

### Secret & API Key Hunting
Recursive crawling of JavaScript files to find sensitive tokens.
```bash
# Find JS files and search for secrets (AWS, Google, etc.)
gau example.com | grep '\.js$' | httpx -sr -scontent -silent | nuclei -t exposures/ -silent
```

### Advanced SSRF & Redirects
Fuzzing for server-side request forgery via open redirects.
```bash
# Extract parameters and test for SSRF
waybackurls example.com | grep '=' | qsreplace "http://burpcollaborator.net" | httpx -silent -status-code -location
```

---

## 🤖 Autonomous AI Reasoning (Agentic Mode)

The `darkwin hunt` command utilizes an **Agentic Loop** that mimics a human researcher's decision-making process.

### How it Works:
1.  **Observation**: The agent analyzes the initial target (tech stack, subdomains, open ports).
2.  **Hypothesis**: Based on the observation, it forms a hypothesis (e.g., "The target uses an old version of Apache, it might be vulnerable to CVE-2021-41773").
3.  **Action**: It selects the most appropriate module (e.g., `nuclei` with a specific template).
4.  **Verification**: It analyzes the output. If a finding is found, it validates it; otherwise, it adjusts its strategy and loops back to step 1.

### Tuning the Agent
```bash
# Increase depth for highly complex targets
darkwin hunt example.com --max-steps 50

# Limit the agent to specific vulnerability classes
darkwin hunt example.com --tags "sqli,rce,ssrf"
```

---

## 🔧 Advanced Troubleshooting & Self-Healing

The `darkwin doctor` command is more than a simple check; it is an automated repair engine.

### Automated Healing Workflows
When run with the `--fix` flag, the platform performs:
- **Dependency Repair**: Re-installs missing binaries or Python packages.
- **Permission Correction**: Safely resets `chmod` and `chown` on log and screenshot directories.
- **Schema Synchronization**: Detects and applies missing database migrations.
- **Template Sync**: Forces a refresh of vulnerability signatures (Nuclei/Custom).

```bash
# Perform a full system "Health Check & Repair"
darkwin doctor --fix

# Install missing external bug bounty tools (dalfox, gau, qsreplace)
make setup-tools
```

---

## 🔬 Anatomy of a Vulnerability Scan

When you execute `darkwin scan`, the platform orchestrates a 4-phase assault to ensure no stone is left unturned.

### Phase 1: Attack Surface Mapping
- **Crawling & Spidering**: Automated discovery of all visible pages and assets.
- **Endpoint Discovery**: Fuzzing for hidden directories (e.g., `/admin`, `/.git`).
- **JS Analysis**: Deep-parsing of JavaScript bundles to find hidden APIs and hardcoded secrets.
- **AI Fuzzing**: Utilizing mutation-based fuzzing to discover unusual input handling.

### Phase 2: Web Logic & Client-Side
- Testing for XSS (Reflected/Stored/DOM), CSRF, Open Redirects, and Clickjacking.
- Automated validation of security headers (CSP, HSTS, XFO).

### Phase 3: Injection & Data Integrity
- Massive-scale testing for SQLi, NoSQLi, SSTI, and Command Injection.
- Specialized GraphQL introspection and mutation testing.

### Phase 4: File & Server Security
- Path traversal (LFI/RFI) and File Upload bypass testing.
- RCE fingerprinting and server misconfiguration audits.

---

## 🕸️ Distributed Mesh Architecture (Advanced)

DARKWIN-NGASR is designed to run across multiple nodes for massive horizontal scaling.

### Node Roles:
- **Primary Node**: Orchestrates the mesh, manages the database, and provides the CLI/Dashboard.
- **Worker Nodes**: Headless instances that receive tasks from the Redis queue and execute pipelines.

### Scaling Workflow:
1.  Launch the primary node with `make docker-up`.
2.  Deploy worker nodes on remote servers pointing to the primary's `REDIS_URL`.
3.  Monitor global health with `darkwin mesh`.

---

## 🛠️ Custom Module SDK (Extending DARKWIN)

The platform is modular. You can add your own scanning logic by creating a Python file in `modules/vulnerability_engine/custom/`.

### Basic Module Requirements:
- Must define `MODULE_META` dictionary (name, description, etc.).
- Must implement `async def run(url, scan_id, config)`.
- Must return a list of finding dictionaries.

See **[Module Development Guide](../../docs/dev/MODULES.md)** for the full specification.

---
<div align="center">
<b>DARKWIN-NGASR | Autonomous · Distributed · Stealthy</b>
</div>
