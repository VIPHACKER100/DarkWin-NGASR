# 🌌 DARKWIN — Next-Gen Automated Security Research

# 🌌 DARKWIN — Next-Gen Automated Security Research

### Developed by ARYAN AHIRWAR (VIPHACKER.100)

**Version 1.0.0 — FULL RELEASE**

DARKWIN is an elite, fully autonomous security research platform designed for bug bounty hunters and red teamers. It combines traditional scanning techniques with advanced AI reasoning and 117+ specialized modules. All wordlists and payloads are now fully populated and verified for production use.

---

## 🚀 Get Started

1.  **Installation & Diagnosis**:
    ```bash
    bash setup.sh
    # Verify environment and fix missing dependencies
    python core/darkwin.py doctor --fix
    ```

2.  **Configuration**:
    ```bash
    # Run interactive setup wizard
    python core/darkwin.py setup
    ```

3.  **Initialize Database**:
    ```bash
    python core/migrations/init_db.py
    ```

4.  **Launch Dashboard**:
    ```bash
    # Start the API backend
    cd dashboards/backend && python app.py
    # Start the Next.js frontend
    cd dashboards/frontend-next && npm run dev
    ```

5.  **Run Your First Scan**:
    ```bash
    darkwin recon example.com --scope-file scope.json
    ```

---

## 🛠️ Platform Features

*   **System Doctor**: Automated environment self-healing with `doctor --fix`.
*   **Async Pipeline Engine**: High-performance parallel execution of scanning modules.
*   **Next.js Dashboard**: Premium, real-time web interface for scan management.
*   **AI Integration**: Autonomous vulnerability classification and payload generation.
*   **117+ Specialized Modules**: Covering reconnaissance, fuzzing, and exploit research.

---

## Overview

DARKWIN is a comprehensive, modular security research automation platform featuring 500+ scan modules, AI-powered vulnerability classification, distributed scanning, and a full-featured web dashboard. It orchestrates reconnaissance, web scanning, vulnerability detection, fuzzing, network analysis, cloud security audits, and exploit research into unified pipelines.

## Prerequisites

- **Python 3.11+**
- **PostgreSQL 15+**
- **Redis 7+**
- **Node.js 20+** (for dashboard frontend)
- External tools: `nmap`, `subfinder`, `httpx`, `nuclei`, `ffuf`, `amass`, `katana`, `sqlmap`, `dalfox`, `masscan`

## Quick Start

```bash
# 1. Clone and enter the repository
git clone <repo-url> && cd DARKWIN

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install external tools
bash setup.sh

# 4. Configure
cp config.yaml.example config.yaml
# Edit config.yaml with your database URL, API keys, etc.

# 5. Initialize database
python core/migrations/init_db.py

# 6. Run the CLI
darkwin --help

# 7. Start the dashboard (optional)
docker-compose up -d
```

## Architecture

```
DARKWIN/
├── core/                  # Engine, config, logging, CLI, pipeline, scheduler
├── modules/               # 500+ scan modules (recon, web, vuln, network, cloud, exploit)
│   ├── reconnaissance/    # Subdomain, DNS, WHOIS, ASN, CT, dorking
│   ├── attack_surface/    # Asset mapping, service ID, API detection
│   ├── web_scanning/      # Crawler, JS analysis, param/endpoint discovery
│   ├── vulnerability_engine/  # SQLi, XSS, CSRF, LFI, RFI, SSTI, CMDi, RCE, cloud
│   ├── fuzzing/           # Directory, API, GraphQL, parameter fuzzing
│   ├── network/           # Port scanning, service enum, SSL analysis
│   ├── exploit_engine/    # CVE matching, exploit search, payload suggestions
│   ├── post_exploitation/ # Privesc, credential access, persistence analysis
│   ├── reporting/         # HTML, Markdown, bug bounty report generation
│   └── cloud_security/    # IAM, bucket, misconfig scanning
├── pipelines/             # Orchestrated scan workflows
├── ai/                    # LLM-powered vuln classification & payload generation
├── automation/            # Auto hunter, distributed scanning
├── integrations/          # Shodan, Censys, VirusTotal, GitHub
├── dashboards/            # Flask backend + React/Next.js frontend
├── wordlists/             # Subdomain, directory, parameter wordlists
├── payloads/              # XSS, SQLi, LFI, SSTI, fuzzing payloads
├── logs/                  # Scan and system logs
├── reports/               # Generated reports and screenshots
└── tests/                 # Unit and integration tests
```

## CLI Commands

```bash
darkwin setup                    # Run interactive configuration wizard
darkwin doctor                   # Run system diagnostics (--fix to repair)
darkwin recon <target>           # Run reconnaissance pipeline (Async)
darkwin scan <target>            # Run vulnerability scan pipeline
darkwin hunt <target>            # Full bug bounty pipeline (Orchestrated)
darkwin report <scan_id>         # Generate findings reports
darkwin modules                  # List all available modules
```

---

## Legal Disclaimer

This tool is provided for **educational and authorized security testing purposes only**. The authors are not responsible for any misuse. Always obtain explicit written authorization before testing any system. See [LEGAL.md](LEGAL.md) for full terms.

---

## License

MIT License — © 2026 **ARYAN AHIRWAR (VIPHACKER.100)**
